import re
from datetime import UTC, datetime
from typing import Annotated, Any, TypedDict, Literal
from pydantic import BaseModel, Field
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from domain.ports import AIPort, DatabasePort, MessagingPort
from domain.enums import LeadStatus
from infrastructure.logging import get_logger
from config.settings import settings

logger = get_logger(__name__)

class IntentExtraction(BaseModel):
    """Structured information about user intent."""
    budget: int | None = Field(default=None, description="The maximum budget expressed by the user in Euro.")
    intent: Literal["VISIT", "PURCHASE", "INFO", "OTHER"] = Field(description="The primary intent of the user.")
    entities: list[str] = Field(default_factory=list, description="Relevant entities like locations or property types mentioned.")

class PropertyPreferences(BaseModel):
    """Structured information about user property preferences."""
    rooms: list[int] = Field(default_factory=list, description="Preferred number of rooms.")
    zones: list[str] = Field(default_factory=list, description="Preferred neighborhoods or zones.")
    features: list[str] = Field(default_factory=list, description="Specific features like 'balcony', 'garage', etc.")
    property_types: list[str] = Field(default_factory=list, description="Types of property like 'apartment', 'villa'.")

class SentimentAnalysis(BaseModel):
    """Analysis of user sentiment and urgency."""
    sentiment: Literal["POSITIVE", "NEUTRAL", "NEGATIVE", "ANGRY"] = Field(description="Detected sentiment.")
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
    status_msg: str
    ai_response: str
    source: Literal["WEB_APPRAISAL", "PORTAL", "WHATSAPP", "UNKNOWN"]
    context_data: dict[str, Any]
    checkpoint: Literal["cache_hit", "human_mode", "continue", "done"]


def create_lead_processing_graph(db: DatabasePort, ai: AIPort, msg: MessagingPort, journey: Any = None, scraper: Any = None):
    
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
        else:
            # Update name if provided and missing
            if name and not lead.get("customer_name"):
                db.save_lead({"customer_phone": phone, "customer_name": name})
                lead["customer_name"] = name

        # Append user message to history in DB immediately (side effect as per legacy)
        # However, for pure graph we might want to defer. 
        # But LeadProcessor did it before AI status check.
        # We'll stick to legacy behavior for consistency.
        
        if not lead.get("is_ai_active", True):
            return {"lead_data": lead, "checkpoint": "human_mode"}

        # Prepare context
        history = lead.get("messages", [])[-settings.MAX_CONTEXT_MESSAGES:]
        history_text = "\n".join([f"{m.get('role')}: {m.get('content')}" for m in history])
        
        # Detect Source
        source = "WHATSAPP"
        context_data = {}
        
        query_lower = state["user_input"].lower()
        if "valutazione" in query_lower or "appraisal" in query_lower:
            source = "WEB_APPRAISAL"
        elif "immobiliare" in query_lower or "idealista" in query_lower or "agency:" in query_lower:
            source = "PORTAL"
            # Try to extract property context if present
            prop_match = re.search(r"immobile:\s*(.*)", query_lower)
            if prop_match:
                context_data["property_id"] = prop_match.group(1).strip()

        return {
            "lead_data": lead, 
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
            "status_msg": "",
            "ai_response": "",
            "source": source,
            "context_data": context_data
        }

    def intent_node(state: AgentState) -> dict[str, Any]:
        """Structured extraction of intent and entities using LLM."""
        text = state["user_input"]
        phone = state["phone"]
        lead = state["lead_data"]
        
        from infrastructure.adapters.langchain_adapter import LangChainAdapter
        
        # We prefer using the LLM directly if it's a LangChainAdapter for advanced features
        # Otherwise we fallback to the port's generic invoke/generate if it supports structured output
        # To maintain architectural purity, we check if the port provides an 'llm' object.
        
        llm = getattr(ai, "llm", None)
        if llm and hasattr(llm, "with_structured_output"):
            llm_to_use = llm.with_structured_output(IntentExtraction)
        else:
             llm_to_use = ChatMistralAI(
                mistral_api_key=settings.MISTRAL_API_KEY,
                model=settings.MISTRAL_MODEL,
            ).with_structured_output(IntentExtraction)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract structured information from the user message. Language: Italian/English."),
            ("human", "{input}"),
        ])
        
        try:
            extraction = llm_to_use.invoke(prompt.format(input=text))
            
            # Journey Transition
            current_state = lead.get("journey_state") or LeadStatus.ACTIVE
            
            # Phase 1.1: Appraisal -> captured as HOT lead with Tag
            if state["source"] == "WEB_APPRAISAL":
                 if current_state == LeadStatus.ACTIVE:
                     journey.transition_to(phone, LeadStatus.HOT)
            
            if journey and extraction.intent == "VISIT":
                if current_state != LeadStatus.APPOINTMENT_REQUESTED:
                    journey.transition_to(phone, LeadStatus.APPOINTMENT_REQUESTED)
            elif journey and extraction.intent == "PURCHASE":
                 if current_state == LeadStatus.ACTIVE or current_state == LeadStatus.HOT:
                     journey.transition_to(phone, LeadStatus.QUALIFIED)

            return {
                "budget": extraction.budget or lead.get("budget_max"),
                "intent": extraction.intent,
                "entities": extraction.entities
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
                mistral_api_key=settings.MISTRAL_API_KEY,
                model=settings.MISTRAL_MODEL,
            ).with_structured_output(PropertyPreferences)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract property preferences from the conversation history and latest input."),
            ("human", "History: {history}\nLatest: {input}"),
        ])

        try:
            prefs = llm_to_use.invoke(prompt.format(history=state["history_text"], input=state["user_input"]))
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
                mistral_api_key=settings.MISTRAL_API_KEY,
                model=settings.MISTRAL_MODEL,
            ).with_structured_output(SentimentAnalysis)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Analyze user sentiment and urgency from the message."),
            ("human", "{input}"),
        ])

        try:
            analysis = llm_to_use.invoke(prompt.format(input=state["user_input"]))
            return {"sentiment": analysis}
        except Exception as e:
            logger.error("SENTIMENT_ANALYSIS_FAILED", context={"error": str(e)})
            return {"sentiment": state["sentiment"]}
            
    def market_analysis_node(state: AgentState) -> dict[str, Any]:
        """Fetch market data for negotiation context (Phase 5)."""
        if not scraper or state["intent"] != "PURCHASE":
            return {"market_data": {}}
        
        # In a real scenario, we'd use the scraped data to provide context.
        # For now, we simulate market context if a property is in context.
        prop_id = state["context_data"].get("property_id")
        if prop_id:
            logger.info("FETCHING_MARKET_DATA", context={"property": prop_id})
            # Mocking or calling scraper if we had a URL. 
            # If we don't have a URL, we provide generic market trends.
            return {"market_data": {"trend": "stable", "avg_price_sqm": 4500, "area": "Milano"}}
            
        return {"market_data": {}}

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
        if not valid_properties:
             status_msg = "IMPORTANT: No exact matches found above 0.78 threshold. You MUST admit that you couldn't find a perfect match right now, but you are available to help."
        
        return {"retrieved_properties": valid_properties, "status_msg": status_msg}

    def generation_node(state: AgentState) -> dict[str, Any]:
        """Call LLM to generate grounded response using templates."""
        lead = state["lead_data"]
        nm = lead.get("customer_name", "Cliente")
        current_stage = lead.get("journey_state") or LeadStatus.ACTIVE
        details = _format_properties(state["retrieved_properties"])
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", (
                "Identity: Anzevino AI. Goal: Respond helpfully to {name}.\n"
                "Current Journey Stage: {stage}\n"
                "Context History:\n{history}\n"
                "User Sentiment: {sentiment} (Urgency: {urgency})\n"
                "User Preferences: {preferences}\n"
                "Lead Source: {source}\n"
                "Property Context: {context_data}\n"
                "Market Insights: {market_data}\n"
                "Available Properties Data: {properties}\n\n"
                "PHASE SPECIFIC INSTRUCTIONS:\n"
                "1. If Lead Source is WEB_APPRAISAL: Acknowledge the valuation request and provide the estimated range immediately.\n"
                "2. If Lead Source is PORTAL: Mention the specific house from {context_data} and ask if they want to see the floor plan.\n"
                "3. If Journey Stage is APPOINTMENT_REQUESTED: Propose a viewing and provide this scheduling link: https://calendly.com/anzevino/viewing\n"
                "Keep it native for WhatsApp (short, friendly, in Italian unless user speaks English)."
            )),
            ("human", "{input}. {status_msg}"),
        ])
        
        llm = getattr(ai, "llm", None)
        
        if llm:
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
                input=state["user_input"],
                status_msg=state["status_msg"]
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
                input=state["user_input"],
                status_msg=state["status_msg"]
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
                "metadata": {"by": "ai", "graph": "langgraph"}
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
            "context_data": state["context_data"]
        }
        logger.info("FINALIZING_METADATA", context={"metadata": metadata})
        
        update_payload = {
            "customer_phone": phone,
            "metadata": metadata,
            "messages": messages,
            "last_message": response or text,
            "updated_at": datetime.now(UTC).isoformat()
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
    def route_after_ingest(state: AgentState):
        if state["checkpoint"] == "human_mode":
            return END
        return "intent"
    
    workflow.add_conditional_edges("ingest", route_after_ingest)
    
    workflow.add_edge("intent", "preferences")
    workflow.add_edge("preferences", "sentiment")
    workflow.add_edge("sentiment", "market_analysis")
    workflow.add_edge("market_analysis", "cache_check")
    
    # Conditional edge from cache_check
    def route_after_cache(state: AgentState):
        if state["checkpoint"] == "cache_hit":
            return "finalize"
        return "retrieval"
        
    workflow.add_conditional_edges("cache_check", route_after_cache)
    
    workflow.add_edge("retrieval", "generation")
    workflow.add_edge("generation", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()


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
