import re
from datetime import UTC, datetime
from typing import Any, Literal, TypedDict, cast

from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field, SecretStr

from config.settings import settings
from domain.enums import LeadStatus
from domain.ports import AIPort, CalendarPort, DatabasePort, MessagingPort
from domain.services.logging import get_logger

logger = get_logger(__name__)


class IntentExtraction(BaseModel):
    """Structured information about user intent."""

    budget: int | None = Field(
        default=None, description="The maximum budget expressed by the user in Euro."
    )
    intent: Literal["VISIT", "PURCHASE", "INFO", "OTHER"] = Field(
        description="The primary intent of the user."
    )
    entities: list[str] = Field(
        default_factory=list,
        description="Relevant entities like locations or property types mentioned.",
    )


class PropertyPreferences(BaseModel):
    """Structured information about user property preferences."""

    rooms: list[int] = Field(default_factory=list, description="Preferred number of rooms.")
    zones: list[str] = Field(default_factory=list, description="Preferred neighborhoods or zones.")
    features: list[str] = Field(
        default_factory=list, description="Specific features like 'balcony', 'garage', etc."
    )
    property_types: list[str] = Field(
        default_factory=list, description="Types of property like 'apartment', 'villa'."
    )


class SentimentAnalysis(BaseModel):
    """Analysis of user sentiment and urgency."""

    sentiment: Literal["POSITIVE", "NEUTRAL", "NEGATIVE", "ANGRY"] = Field(
        description="Detected sentiment."
    )
    urgency: Literal["HIGH", "MEDIUM", "LOW"] = Field(description="Detected urgency.")
    notes: str = Field(description="Brief explanation of the mood.")


class AgentState(TypedDict):
    """The state of our lead processing graph."""

    phone: str
    user_input: str
    name: str | None
    postcode: str | None
    lead_data: dict[str, Any]
    history_text: str
    embedding: list[float] | None
    budget: int | None
    intent: str | None
    entities: list[str]
    preferences: PropertyPreferences
    sentiment: SentimentAnalysis
    retrieved_properties: list[dict[str, Any]]
    market_data: dict[str, Any]
    negotiation_data: dict[str, Any]
    status_msg: str
    ai_response: str
    source: Literal["WEB_APPRAISAL", "PORTAL", "WHATSAPP", "UNKNOWN"]
    context_data: dict[str, Any]
    checkpoint: Literal["cache_hit", "human_mode", "continue", "done"]
    language: Literal["it", "en"]


def create_lead_processing_graph(
    db: DatabasePort,
    ai: AIPort,
    msg: MessagingPort,
    journey: Any = None,
    scraper: Any = None,
    market: Any = None,
    calendar: CalendarPort | None = None,
) -> Any:
    def ingest_node(state: AgentState) -> dict[str, Any]:
        """Fetch lead data and prepare basic state."""
        phone = state["phone"]
        name = state.get("name")
        postcode = state.get("postcode")
        lead = db.get_lead(phone)

        if not lead:
            lead = {
                "customer_phone": phone,
                "customer_name": name or "Cliente",
                "postcode": postcode,
                "status": LeadStatus.ACTIVE,
                "journey_state": LeadStatus.ACTIVE,
                "is_ai_active": True,
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            }
            db.save_lead(lead)
            lead = db.get_lead(phone) or lead
        # Update name if provided and missing
        elif name and not lead.get("customer_name"):
            db.save_lead({"customer_phone": phone, "customer_name": name})
            lead["customer_name"] = name

        # Append user message to history in DB immediately (side effect as per legacy)
        # However, for pure graph we might want to defer.
        # But LeadProcessor did it before AI status check.
        # We'll stick to legacy behavior for consistency.

        if not lead.get("is_ai_active", True):
            return {"lead_data": lead, "checkpoint": "human_mode"}

        # Prepare context
        history = lead.get("messages", [])[-settings.MAX_CONTEXT_MESSAGES :]
        history_text = "\n".join([f"{m.get('role')}: {m.get('content')}" for m in history])

        # Detect Source
        source = state.get("source") or "WHATSAPP"
        context_data = state.get("context_data") or {}

        query_lower = state["user_input"].lower()
        # Only run heuristic if source is still WHATSAPP (default)
        if source == "WHATSAPP":
            if "valutazione" in query_lower or "appraisal" in query_lower:
                source = "WEB_APPRAISAL"
            elif (
                "immobiliare" in query_lower
                or "idealista" in query_lower
                or "agency:" in query_lower
            ):
                source = "PORTAL"
                # Try to extract property context if present
                prop_match = re.search(r"immobile:\s*(.*)", query_lower)
                if prop_match:
                    context_data["property_id"] = prop_match.group(1).strip()

        # Language Detection
        # 1. Grounding via phone (+39 is Italian, everything else defaults to English for Tourists)
        is_italian_number = phone.startswith("+39") or phone.startswith("39")

        # 2. Heuristic check on input
        english_keywords = [
            "hello",
            "hi",
            "info",
            "details",
            "property",
            "house",
            "buy",
            "rent",
            "price",
        ]
        is_english_input = any(word in query_lower for word in english_keywords)

        language = "it" if is_italian_number and not is_english_input else "en"

        return {
            "lead_data": lead,
            "language": language,
            "history_text": history_text,
            "checkpoint": "continue",
            "embedding": None,
            "budget": None,
            "intent": None,
            "entities": [],
            "preferences": PropertyPreferences(),
            "sentiment": SentimentAnalysis(sentiment="NEUTRAL", urgency="LOW", notes="Init"),
            "retrieved_properties": [],
            "market_data": {},
            "negotiation_data": {},
            "status_msg": "",
            "ai_response": "",
            "source": source,
            "context_data": context_data,
        }

    def intent_node(state: AgentState) -> dict[str, Any]:
        """Structured extraction of intent and entities using LLM."""
        text = state["user_input"]
        phone = state["phone"]
        lead = state["lead_data"]

        # We prefer using the LLM directly if it's a LangChainAdapter for advanced features
        # Otherwise we fallback to the port's generic invoke/generate if it supports structured output
        # To maintain architectural purity, we check if the port provides an 'llm' object.

        llm = getattr(ai, "llm", None)
        if llm and hasattr(llm, "with_structured_output"):
            llm_to_use = llm.with_structured_output(IntentExtraction)
        else:
            llm_to_use = ChatMistralAI(
                api_key=SecretStr(settings.MISTRAL_API_KEY),
                model_name=settings.MISTRAL_MODEL,
            ).with_structured_output(IntentExtraction)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Extract structured information from the user message. Language: Italian/English.",
                ),
                ("human", "{input}"),
            ]
        )

        try:
            extraction = llm_to_use.invoke(prompt.format(input=text))

            # Journey Transition
            current_state = lead.get("journey_state") or LeadStatus.ACTIVE

            # Phase 1.1: Appraisal -> captured as HOT lead with Tag
            if state["source"] == "WEB_APPRAISAL":
                if current_state == LeadStatus.ACTIVE:
                    journey.transition_to(phone, LeadStatus.HOT)

            # Update lead_data in state so subsequent nodes see the change
            updated_lead = lead.copy()
            if journey and extraction.intent == "VISIT":
                if current_state != LeadStatus.APPOINTMENT_REQUESTED:
                    journey.transition_to(phone, LeadStatus.APPOINTMENT_REQUESTED)
                    updated_lead["journey_state"] = LeadStatus.APPOINTMENT_REQUESTED
            elif journey and extraction.intent == "PURCHASE":
                if current_state == LeadStatus.ACTIVE or current_state == LeadStatus.HOT:
                    journey.transition_to(phone, LeadStatus.QUALIFIED)
                    updated_lead["journey_state"] = LeadStatus.QUALIFIED

            return {
                "budget": extraction.budget or lead.get("budget_max"),
                "intent": extraction.intent,
                "entities": extraction.entities,
                "lead_data": updated_lead,
            }
        except Exception as e:
            logger.error("INTENT_EXTRACTION_FAILED", context={"error": str(e)})
            budget = _extract_budget(text)
            return {"budget": budget or lead.get("budget_max")}

    def preference_extraction_node(state: AgentState) -> dict[str, Any]:
        """Extract detailed property preferences from history and input."""
        llm = getattr(ai, "llm", None)
        if llm and hasattr(llm, "with_structured_output"):
            llm_to_use = llm.with_structured_output(PropertyPreferences)
        else:
            llm_to_use = ChatMistralAI(
                api_key=SecretStr(settings.MISTRAL_API_KEY),
                model_name=settings.MISTRAL_MODEL,
            ).with_structured_output(PropertyPreferences)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Extract property preferences from the conversation history and latest input.",
                ),
                ("human", "History: {history}\nLatest: {input}"),
            ]
        )

        try:
            prefs = llm_to_use.invoke(
                prompt.format(history=state["history_text"], input=state["user_input"])
            )
            return {"preferences": prefs}
        except Exception as e:
            logger.error("PREFERENCE_EXTRACTION_FAILED", context={"error": str(e)})
            return {"preferences": state["preferences"]}

    def sentiment_analysis_node(state: AgentState) -> dict[str, Any]:
        """Analyze user sentiment and urgency."""
        llm = getattr(ai, "llm", None)
        if llm and hasattr(llm, "with_structured_output"):
            llm_to_use = llm.with_structured_output(SentimentAnalysis)
        else:
            llm_to_use = ChatMistralAI(
                api_key=SecretStr(settings.MISTRAL_API_KEY),
                model_name=settings.MISTRAL_MODEL,
            ).with_structured_output(SentimentAnalysis)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Analyze user sentiment and urgency from the message."),
                ("human", "{input}"),
            ]
        )

        try:
            analysis = llm_to_use.invoke(prompt.format(input=state["user_input"]))
            return {"sentiment": analysis}
        except Exception as e:
            logger.error("SENTIMENT_ANALYSIS_FAILED", context={"error": str(e)})
            return {"sentiment": state["sentiment"]}

    def market_analysis_node(state: AgentState) -> dict[str, Any]:
        """Fetch real market data for valuations (Appraisal) or negotiations."""
        market_results = {}

        # Scenario 1: WEB_APPRAISAL (Valuation request)
        if state["source"] == "WEB_APPRAISAL":
            # Extract town/zone from context or postcode
            postcode = state.get("postcode")
            # If we don't have a clear zone, we try to guess from entities or prompt extraction
            zone = state["entities"][0] if state["entities"] else postcode

            if zone and market:
                avg = market.get_avg_price(zone)
                # Also fetch competitive stats from our own ingested data via DB
                stats = db.get_market_stats(zone)

                if avg or stats:
                    market_results = {
                        "avg_price_sqm": avg or stats.get("avg_price_sqm"),
                        "area": zone,
                        "competitive_stats": stats,
                        "estimate_range": f"€{int((avg or stats.get('avg_price_sqm', 0)) * 0.9):,} - €{int((avg or stats.get('avg_price_sqm', 0)) * 1.1):,}",
                    }

        # Scenario 2: Negotiation (Phase 5)
        elif scraper and state["intent"] == "PURCHASE":
            prop_id = state["context_data"].get("property_id")
            if prop_id:
                logger.info("FETCHING_NEGOTIATION_DATA", context={"property": prop_id})
                # In a real case, we might fetch the property from DB first to get the URL
                # properties = db.get_property_by_id(prop_id)
                # But for now, we'll simulate insights
                market_results = market.get_market_insights(
                    state["entities"][0] if state["entities"] else "Milano"
                )

        return {"market_data": market_results, "negotiation_data": market_results}

    def cache_check_node(state: AgentState) -> dict[str, Any]:
        """Check semantic cache."""
        embedding = ai.get_embedding(state["user_input"])
        cached = db.get_cached_response(embedding)

        if cached:
            return {"ai_response": cached, "checkpoint": "cache_hit", "embedding": embedding}
        return {"embedding": embedding, "checkpoint": "continue"}

    def retrieval_node(state: AgentState) -> dict[str, Any]:
        """Fetch matching properties."""
        query = state["user_input"]
        embedding = state["embedding"]
        budget = state["budget"]

        filters = {"max_price": budget} if budget else {}
        properties = db.get_properties(query, embedding=embedding, filters=filters)

        # Filter (ADR-004 logic: 0.78 threshold)
        valid_properties = [p for p in properties if p.get("similarity", 0) >= 0.78]
        status_msg = ""

        # Fallback Mechanism: If no exact matches, take the best ones with a warning
        if not valid_properties:
            # Take top 2 if they exist, even if below threshold
            fallback_properties = properties[:2]
            if fallback_properties:
                valid_properties = fallback_properties
                status_msg = "No exact matches found above 0.78. Showing closest alternatives. Mention these might not be perfect matches but are the best available."
            elif state["intent"] != "VISIT":
                status_msg = "No properties found at all. Admit this politely but remain helpful."

        return {"retrieved_properties": valid_properties, "status_msg": status_msg}

    def generation_node(state: AgentState) -> dict[str, Any]:
        """Call LLM to generate grounded response using templates."""
        lead = state["lead_data"]
        nm = lead.get("customer_name", "Cliente")
        current_stage = lead.get("journey_state") or LeadStatus.ACTIVE
        details = _format_properties(state["retrieved_properties"])

        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "Identity: Anzevino AI. Goal: Respond helpfully to {name}.\n"
                        "Current Journey Stage: {stage}\n"
                        "Context History:\n{history}\n"
                        "User Sentiment: {sentiment} (Urgency: {urgency})\n"
                        "User Preferences: {preferences}\n"
                        "Lead Source: {source}\n"
                        "Property Context: {context_data}\n"
                        "Market Insights: {market_data}\n"
                        "Negotiation Data: {negotiation_data}\n"
                        "Available Properties Data: {properties}\n\n"
                        "Language: {language}\n\n"
                        "If Language is 'it': Short, friendly Italian, local agency vibe.\n"
                        "If Language is 'en': Act as a professional, welcoming guide for tourists. Focus on the charm of Tuscany. Explain local nuances like 'borgo', 'agriturismo', and the lifestyle. Use warm, descriptive language.\n\n"
                        "### NEGOTIATION & MARKET INTELLIGENCE ###\n"
                        "If Market Insights (Market Data) are present:\n"
                        "- Explicitly mention the area average price if relevant (e.g., 'The average in {area_name} is €{avg_price_sqm}/sqm').\n"
                        "- Compare the selected properties with the area average.\n"
                        "- If a property is Significantly BELOW the area average, highlight it as a 'potential deal' or 'great value'.\n"
                        "- If it's ABOVE, use data to justify why (e.g., premium features, renovation) or suggest it's a premium option.\n\n"
                        "### CRITICAL PHASE INSTRUCTIONS ###\n"
                        "You MUST follow these instructions based on current state (Stage: {stage}):\n"
                        "1. If Lead Source is WEB_APPRAISAL: Acknowledge the valuation request and provide the estimated range immediately. Use the market average to ground your estimate.\n"
                        "2. If Lead Source is PORTAL: Mention the specific house from {context_data} and ask if they want to see the floor plan.\n"
                        "3. If status_msg mentions 'closest alternatives': Be transparent that these might not match all criteria but are high-quality options in the desired area.\n"
                        "Keep it native for WhatsApp (short, friendly, max 1500 characters, in the detected language: {language})."
                    ),
                ),
                ("human", "{input}"),
            ]
        )

        llm = getattr(ai, "llm", None)

        if llm:
            # Final input assembly
            final_input = state["user_input"]
            if current_stage == "appointment_requested":
                booking_link = settings.SETMORE_LINK
                final_input += f"\n\n(IMPORTANT: The user wants a visit. Suggest booking via this link: {booking_link})"
                if calendar:
                    # In a real scenario, we'd fetch availability for the next few days
                    # slots = calendar.get_availability(settings.SETMORE_STAFF_ID, datetime.now().strftime("%d-%m-%Y"))
                    final_input += "\nNote: The system is ready to sync with your calendar for real-time availability."

            if "foto" in state["user_input"].lower() or "dettagli" in state["user_input"].lower():
                final_input += "\n(Note: The system will automatically generate and send a professional PDF brochure for this property if relevant.)"

            if state["status_msg"]:
                final_input += f"\n\n[ADMIN NOTE: {state['status_msg']}]"

            messages = prompt_template.format_messages(
                name=nm,
                stage=current_stage,
                history=state["history_text"],
                sentiment=state["sentiment"].sentiment,
                urgency=state["sentiment"].urgency,
                preferences=state["preferences"].model_dump_json(),
                properties=details,
                source=state["source"],
                context_data=state["context_data"],
                market_data=state["market_data"],
                area_name=state["market_data"].get("area", "this area"),
                avg_price_sqm=state["market_data"].get("avg_price_sqm", "N/A"),
                negotiation_data=state["negotiation_data"],
                input=final_input,
                language=state["language"],
            )
            response = llm.invoke(messages)
            return {"ai_response": str(response.content)}
        else:
            # Fallback to port's generate_response
            prompt = prompt_template.format(
                name=nm,
                stage=current_stage,
                history=state["history_text"],
                sentiment=state["sentiment"].sentiment,
                urgency=state["sentiment"].urgency,
                preferences=state["preferences"].model_dump_json(),
                properties=details,
                source=state["source"],
                context_data=state["context_data"],
                market_data=state["market_data"],
                negotiation_data=state["negotiation_data"],
                input=state["user_input"],
                language=state["language"],
            )
            response = ai.generate_response(prompt)
            return {"ai_response": response}

    def finalize_node(state: AgentState) -> dict[str, Any]:
        """Perform side effects: sending message, updating history, caching, and PERSISTING metadata."""
        phone = state["phone"]
        response = state["ai_response"]
        text = state["user_input"]
        embedding = state["embedding"]
        lead = state["lead_data"]

        # 1. Update History State
        # We append both user and assistant messages for full persistence
        messages = lead.get("messages") or []
        user_msg = {"role": "user", "content": text, "timestamp": datetime.now(UTC).isoformat()}
        messages.append(user_msg)

        if response:
            assistant_msg = {
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now(UTC).isoformat(),
                "metadata": {"by": "ai", "graph": "langgraph"},
            }
            messages.append(assistant_msg)

            # 2. Send Message
            msg.send_message(phone, response)

        # 3. Update Cache (if not a hit)
        if state["checkpoint"] != "cache_hit" and embedding and response:
            db.save_to_cache(text, embedding, response)

        # 4. Persist Enriched State (Metadata) + New Messages
        metadata = {
            "preferences": state["preferences"].model_dump(),
            "sentiment": state["sentiment"].model_dump(),
            "last_intent": state["intent"],
            "source": state["source"],
            "context_data": state["context_data"],
        }
        logger.info("FINALIZING_METADATA", context={"metadata": metadata})

        update_payload = {
            "customer_phone": phone,
            "metadata": metadata,
            "messages": messages,
            "last_message": response or text,
            "updated_at": datetime.now(UTC).isoformat(),
        }
        db.save_lead(update_payload)

        return {"checkpoint": "done"}

    # Define Graph
    workflow = StateGraph(AgentState)

    workflow.add_node("ingest", ingest_node)
    workflow.add_node("intent", intent_node)
    workflow.add_node("preferences", preference_extraction_node)
    workflow.add_node("sentiment", sentiment_analysis_node)
    workflow.add_node("market_analysis", market_analysis_node)
    workflow.add_node("cache_check", cache_check_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("generation", generation_node)
    workflow.add_node("finalize", finalize_node)

    # Simple Edges
    workflow.add_edge(START, "ingest")

    # Conditional edge from ingest (human mode vs continue)
    def route_after_ingest(state: AgentState) -> Literal["intent", "__end__"]:
        if state["checkpoint"] == "human_mode":
            return "__end__"
        return "intent"

    workflow.add_conditional_edges("ingest", route_after_ingest)

    workflow.add_edge("intent", "preferences")
    workflow.add_edge("preferences", "sentiment")
    workflow.add_edge("sentiment", "market_analysis")
    workflow.add_edge("market_analysis", "cache_check")

    # Conditional edge from cache_check
    def route_after_cache(state: AgentState) -> Literal["finalize", "retrieval"]:
        if state["checkpoint"] == "cache_hit":
            return "finalize"
        return "retrieval"

    workflow.add_conditional_edges("cache_check", route_after_cache)

    workflow.add_edge("retrieval", "generation")
    workflow.add_edge("generation", "finalize")
    workflow.add_edge("finalize", END)

    return cast(StateGraph[AgentState], workflow.compile())


# Helpers (Mirrored from LeadProcessor)
def _extract_budget(text: str) -> int | None:
    budget_matches = re.findall(
        r"(\d+(?:\.\d+)?)[\s]?(m(?:ln|ilioni)?)|(\d+)[\s]?k|(\d{5,})", text.lower()
    )
    if budget_matches:
        found_budgets = []
        for m_val, _m_unit, k_val, raw_val in budget_matches:
            if m_val:
                val = int(float(m_val) * 1000000)
            elif k_val:
                val = int(k_val) * 1000
            else:
                val = int(raw_val)
            found_budgets.append(val)
        return max(found_budgets)
    return None


def _format_properties(properties: list[dict[str, Any]]) -> str:
    if not properties:
        return "Nessun immobile trovato."
    res = "Opzioni trovate:\n"
    for p in properties:
        res += f"- {p.get('title')}: €{p.get('price'):,}\n"
    return res
