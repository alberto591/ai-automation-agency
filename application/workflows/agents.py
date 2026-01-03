import re
from datetime import UTC, datetime
from typing import Any, Literal, TypedDict, cast

from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field, SecretStr

from application.services.lead_scoring_service import LeadScoringService
from config.settings import settings
from domain.enums import LeadStatus
from domain.handoff import HandoffReason, HandoffRequest
from domain.ports import AIPort, CalendarPort, DatabasePort, MessagingPort
from domain.qualification import Intent, QualificationData
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
    source: Literal["FIFI_APPRAISAL", "PORTAL", "WHATSAPP", "UNKNOWN"]
    context_data: dict[str, Any]
    checkpoint: Literal["cache_hit", "human_mode", "continue", "done"]
    language: Literal["it", "en"]
    fifi_data: dict[str, Any]  # Appraisal results
    qualification_data: dict[str, Any]  # Serialized QualificationData
    lead_score: dict[str, Any]  # Serialized LeadScore


def create_lead_processing_graph(
    db: DatabasePort,
    ai: AIPort,
    msg: MessagingPort,
    journey: Any = None,
    scraper: Any = None,
    market: Any = None,
    calendar: CalendarPort | None = None,
    validation: Any = None,
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
                source = "FIFI_APPRAISAL"
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
            "fifi_data": {},
            "qualification_data": lead.get("metadata", {}).get("qualification_data", {}),
            "lead_score": lead.get("metadata", {}).get("lead_score", {}),
        }

    def fifi_appraisal_node(state: AgentState) -> dict[str, Any]:
        """
        Dedicated node for Fifi AI appraisal processing.
        Handles ML inference, uncertainty quantification, and human oversight routing.
        """
        if state["source"] != "FIFI_APPRAISAL":
            return {"fifi_data": {}}

        logger.info("FIFI_APPRAISAL_START", context={"phone": state["phone"]})

        # Lazy imports for ML components
        from infrastructure.ml.feature_engineering import (
            extract_property_features,
        )
        from infrastructure.ml.xgboost_adapter import XGBoostAdapter

        # 1. Extract features from user input
        features = extract_property_features(
            description=state["user_input"], address=state["lead_data"].get("address")
        )

        # 2. ML Prediction (Model Simulator for Week 3)
        adapter = XGBoostAdapter()
        prediction = adapter.predict(features)

        # 3. Find comparables for uncertainty estimation
        # We use existing retrieved properties if any, or fetch new ones
        comparables = db.get_properties(state["user_input"], use_mock_table=True, limit=5)
        uncertainty_score = adapter.calculate_uncertainty(prediction, comparables)

        # 4. Confidence interval
        confidence_low = int(prediction * (1 - uncertainty_score))
        confidence_high = int(prediction * (1 + uncertainty_score))

        # 5. Human oversight decision
        status = "AUTO_APPROVED"
        if uncertainty_score > 0.15:
            status = "HUMAN_REVIEW_REQUIRED"

        # High Value Trigger (Safety Check)
        if prediction > 2000000:
            status = "HUMAN_REVIEW_REQUIRED"
            logger.warning("HIGH_VALUE_TRIGGER", context={"value": prediction})

        # 6. Calculate investment metrics
        investment_metrics = adapter.calculate_investment_metrics(
            property_value=prediction,
            sqm=features.sqm,
            zone=features.zone_slug,
        )

        fifi_res = {
            "fifi_status": status,
            "uncertainty_score": uncertainty_score,
            "predicted_value": int(prediction),
            "confidence_range": f"€{int(confidence_low or 0):,} - €{int(confidence_high or 0):,}",
            "confidence_level": int((1 - uncertainty_score) * 100),
            "comparables": comparables[:3],
            "investment_metrics": investment_metrics,
        }

        # 7. Audit Trail Logging
        if validation:
            try:
                validation.log_validation(
                    predicted_value=int(prediction),
                    actual_value=0,  # Not available yet for live audit
                    metadata={
                        "phone": state["phone"],
                        "features": features.model_dump()
                        if hasattr(features, "model_dump")
                        else str(features),
                        "source": "live_appraisal",
                        "user_input": state["user_input"],
                        "zone": features.zone_slug or "UNKNOWN",
                        "city": "UNKNOWN",  # Could extract from features if needed
                        "fifi_status": status,
                    },
                    uncertainty_score=uncertainty_score,
                )
                logger.info("AUDIT_LOG_SUCCESS", context={"phone": state["phone"]})
            except Exception as e:
                logger.error("AUDIT_LOG_FAILED", context={"error": str(e)})

        # Tag lead as HOT and add appraisal notes
        if journey and status == "AUTO_APPROVED":
            journey.transition_to(state["phone"], LeadStatus.HOT)

        return {"fifi_data": fifi_res}

    def handoff_node(state: AgentState) -> dict[str, Any]:
        """
        Handles the transfer of a lead to a human agent.
        Notifies the agency and updates the lead status.
        """
        logger.info("HANDOFF_TRIGGERED", context={"phone": state["phone"]})

        # Lazy import adapter
        from infrastructure.adapters.notification_adapter import NotificationAdapter

        notifier = NotificationAdapter()

        # Determine Reason
        reason = HandoffReason.UNCERTAINTY
        priority = "normal"
        fifi_data = state.get("fifi_data", {})

        if fifi_data.get("predicted_value", 0) > 2000000:
            reason = HandoffReason.HIGH_VALUE
            priority = "urgent"
        elif fifi_data.get("uncertainty_score", 0) > 0.15:
            reason = HandoffReason.UNCERTAINTY
        elif state["sentiment"].sentiment == "ANGRY":
            reason = HandoffReason.SENTIMENT
            priority = "urgent"
        elif "agent" in state["user_input"].lower() or "human" in state["user_input"].lower():
            reason = HandoffReason.USER_REQUEST

        # Construct Request
        req = HandoffRequest(
            lead_id=state["lead_data"]["id"],  # Assuming ID is present
            reason=reason,
            priority=priority,
            user_message=state["user_input"],
            ai_analysis=f"Uncertainty: {fifi_data.get('uncertainty_score', 0):.2f}, Value: €{fifi_data.get('predicted_value', 0):,}",
            metadata={"fifi_data": fifi_data},
        )

        # Notify
        notifier.notify_agency(req)

        # Generate User Message
        msg = (
            "⚠️ Per garantirti la massima precisione, ho inoltrato la tua richiesta a un nostro Senior Agent.\n"
            "Il valore del tuo immobile richiede un'analisi approfondita.\n"
            "Ti contatteremo entro 1 ora al numero fornito."
        )

        return {"ai_response": msg, "checkpoint": "done", "status_msg": "Handed off to human agent"}

    def lead_qualification_node(state: AgentState) -> dict[str, Any]:  # noqa: PLR0912
        """
        Drives the 7-Step Lead Qualification conversational flow.
        Uses LeadScoringService for logic and templates.
        """
        logger.info("LEAD_QUALIFICATION_START", context={"phone": state["phone"]})

        # Hydrate domain object from state dict
        valid_data = state["qualification_data"] or {}
        # Ensure 'intent' is mapped correctly from string to Enum if needed
        # Pydantic handles string->Enum conversion usually
        try:
            qual_data = QualificationData(**valid_data)
        except Exception:
            qual_data = QualificationData()

        # 1. Check what the LAST question was (to parse answer)
        # We assume the user has just answered the 'current' missing field.
        # So we check what is missing essentially.
        current_q_to_answer = LeadScoringService.get_next_question(qual_data)

        if current_q_to_answer:
            # We are mid-flow, so the user_input is the ANSWER to current_q_to_answer
            field = current_q_to_answer["field_name"]
            answer_text = state["user_input"]

            logger.info("PARSING_QUALIFICATION_ANSWER", context={"field": field})

            from pydantic import SecretStr

            # Use LLM to extract structured answer
            extracted_value = _extract_qualification_field(
                field,
                answer_text,
                SecretStr(settings.MISTRAL_API_KEY),
                settings.MISTRAL_MODEL,
            )

            # Update Domain Object
            setattr(qual_data, field, extracted_value)

            # If budget was just asked (<50k check)
            if field == "budget" and extracted_value and extracted_value < 50000:
                logger.warning("LOW_BUDGET_DETECTED", context={"budget": extracted_value})

        # 2. Get NEXT question (after update)
        next_q = LeadScoringService.get_next_question(qual_data)

        if next_q:
            # Ask the next question using strict template
            return {
                "ai_response": next_q["text"],
                "qualification_data": qual_data.model_dump(),
                "checkpoint": "done",  # Skip generation_node
            }
        else:
            # Flow Complete -> Finalize
            logger.info("QUALIFICATION_COMPLETE")
            score = LeadScoringService.calculate_score(qual_data)

            # Update Lead Status
            new_status = LeadStatus.COLD
            if score.category == "HOT":
                new_status = LeadStatus.HOT
            elif score.category == "WARM":
                new_status = LeadStatus.ACTIVE  # WARM usually stays active/nurture
            elif score.category == "DISQUALIFIED":
                new_status = LeadStatus.ARCHIVED  # Or kept active but ignored

            if journey:
                try:
                    journey.transition_to(state["phone"], new_status)
                except Exception as e:
                    logger.warning("JOURNEY_TRANSITION_FAILED", context={"error": str(e)})

            # Generate Summary/Closing message
            completion_msg = ""
            if score.category == "HOT":
                completion_msg = (
                    "Grazie! ✅ Sei un lead HOT! 🔴\n"
                    "Un nostro agente senior ti contatterà tra 5 minuti per mostrarti le migliori opportunità."
                )
            elif score.category == "WARM":
                completion_msg = (
                    "Grazie! Abbiamo registrato le tue preferenze. "
                    "Ti invieremo a breve una selezione di immobili via email."
                )
            else:
                completion_msg = "Grazie per le informazioni. Ti contatteremo se avremo immobili adatti alle tue esigenze."

            return {
                "ai_response": completion_msg,
                "qualification_data": qual_data.model_dump(),
                "lead_score": score.model_dump(),
                "checkpoint": "done",
            }

    def intent_node(state: AgentState) -> dict[str, Any]:  # noqa: PLR0912
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
            if state["source"] == "FIFI_APPRAISAL":
                if current_state == LeadStatus.ACTIVE and journey:
                    journey.transition_to(phone, LeadStatus.HOT)

            # Update lead_data in state so subsequent nodes see the change
            updated_lead = lead.copy()

            # NEW LOGIC: Trigger Qualification Flow if Intent is BUY/SELL/RENT
            # Map Extraction Literal to Domain Enum
            domain_intent = None
            if extraction.intent == "PURCHASE":
                domain_intent = Intent.BUY
            elif extraction.intent == "SALE":  # Future proofing
                domain_intent = Intent.SELL
            elif extraction.intent == "RENTAL":
                domain_intent = Intent.RENT

            if domain_intent in [Intent.BUY, Intent.SELL, Intent.RENT]:
                # Only if not already done or in progress
                if current_state == LeadStatus.ACTIVE:
                    updated_lead["journey_state"] = LeadStatus.QUALIFICATION_IN_PROGRESS

            # Populate qualification_data for conversational continuity
            qual_update = state.get("qualification_data", {}).copy()
            if domain_intent:
                qual_update["intent"] = domain_intent.value
            if extraction.budget:
                qual_update["budget"] = extraction.budget

            return {
                "budget": extraction.budget or lead.get("budget_max"),
                "intent": domain_intent.value if domain_intent else extraction.intent,
                "entities": extraction.entities,
                "lead_data": updated_lead,
                "qualification_data": qual_update,
            }

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
        if state["source"] == "FIFI_APPRAISAL":
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
        """Fetch matching properties using database or tool logic."""
        query = state["user_input"]
        embedding = state["embedding"]
        budget = state["budget"]
        preferences = state["preferences"]

        # Construct filters from preferences
        filters: dict[str, Any] = {}
        if budget:
            filters["max_price"] = budget
        if preferences.property_types:
            filters["property_type"] = preferences.property_types[0]  # Simple taking first for now
        if preferences.rooms:
            filters["min_bedrooms"] = min(preferences.rooms)

        # Use DB port directly (Tool wrapper optional inside node if needed, but direct is cleaner here)
        properties = db.get_properties(query, embedding=embedding, filters=filters, limit=5)

        # Filter (ADR-004 logic: 0.78 threshold)
        valid_properties = [p for p in properties if p.get("similarity", 0) >= 0.78]
        status_msg = ""

        # If explicit search request (e.g. "Show me villas"), relax threshold
        if state["intent"] in ["PURCHASE", "RENT"] or "search" in query.lower():
            if not valid_properties and properties:
                valid_properties = properties[:3]
                status_msg = "Showing best available matches based on your criteria."

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
                        "### OBJECTION HANDLING ###\n"
                        "If the user expresses concerns (price, timing, trust), use the 'Empathy -> Pivot -> Value' technique:\n"
                        "1. Acknowledge and Validate: 'I understand that price is a major factor...'\n"
                        "2. Pivot: 'However, considering the location and recent market trends...'\n"
                        "3. Value: 'This property offers unique investment potential...'\n"
                        "- Never be defensive. Be consultative.\n"
                        "- If they say 'Just looking', encourage them: 'That's the best way to start! I can send you a curated list to get a feel for the market.'\n\n"
                        "### NEGOTIATION & MARKET INTELLIGENCE ###\n"
                        "If Market Insights (Market Data) are present:\n"
                        "- Explicitly mention the area average price if relevant (e.g., 'The average in {area_name} is €{avg_price_sqm}/sqm').\n"
                        "- Compare the selected properties with the area average.\n"
                        "- If a property is Significantly BELOW the area average, highlight it as a 'potential deal' or 'great value'.\n"
                        "- If it's ABOVE, use data to justify why (e.g., premium features, renovation) or suggest it's a premium option.\n\n"
                        "### CRITICAL PHASE INSTRUCTIONS ###\n"
                        "You MUST follow these instructions based on current state (Stage: {stage}):\n"
                        "1. If Lead Source is FIFI_APPRAISAL: Acknowledge the valuation request and provide the estimated range immediately. Use the market average to ground your estimate.\n"
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
                booking_link = settings.CALCOM_BOOKING_LINK
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
                area_name=state["market_data"].get("area", "this area"),
                avg_price_sqm=state["market_data"].get("avg_price_sqm", "N/A"),
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

        # 1. Update History & Persist Messages
        # We save messages one by one using the new save_message method
        user_msg = {
            "role": "user",
            "content": text,
            "timestamp": datetime.now(UTC).isoformat(),
            "metadata": {"source": state["source"]},
        }
        db.save_message(lead["id"], user_msg)

        if response:
            assistant_msg = {
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now(UTC).isoformat(),
                "metadata": {"by": "ai", "graph": "langgraph"},
            }
            db.save_message(lead["id"], assistant_msg)

            # 2. Send Message via Messaging Port
            # Check for Rich Content needed
            # Heuristic: If we retrieved properties and source is WhatsApp, send visual list
            if (
                state["source"] == "WHATSAPP"
                and state.get("retrieved_properties")
                and "list" not in state["status_msg"]  # Avoid loops if we flagging it
            ):
                from domain.messages import InteractiveMessage, Row, Section

                rows = []
                for p in state["retrieved_properties"][:10]:  # Max 10 rows per section
                    rows.append(
                        Row(
                            id=f"prop_{p.get('id', '0')}",
                            title=p.get("title", "Property")[:24],
                            description=f"€{p.get('price', 0):,}",
                        )
                    )

                msg_model = InteractiveMessage(
                    type="list",
                    body_text=response[:1024],  # Truncate body if needed
                    button_text="View Homes",
                    sections=[Section(title="Top Matches", rows=rows)],
                )
                try:
                    msg.send_interactive_message(phone, msg_model)
                except Exception:
                    # Fallback to text if interactive fails (e.g. not implemented in mock)
                    msg.send_message(phone, response)
            else:
                msg.send_message(phone, response)

        # 3. Update Cache (if not a hit)
        if state["checkpoint"] != "cache_hit" and embedding and response:
            db.save_to_cache(text, embedding, response)

        # 4. Persist Enriched Lead Metadata (Excluding full message history)
        metadata = {
            "preferences": state["preferences"].model_dump(),
            "sentiment": state["sentiment"].model_dump(),
            "last_intent": state["intent"],
            "source": state["source"],
            "context_data": state["context_data"],
            "qualification_data": state.get("qualification_data"),
            "lead_score": state.get("lead_score"),
        }
        logger.info("FINALIZING_METADATA", context={"metadata": metadata})

        update_payload = {
            "customer_phone": phone,
            "metadata": metadata,
            "journey_state": lead.get("journey_state"),
            "status": lead.get("status"),
            # "messages" removal here is critical: save_message handled it
            # "last_message" removed - not in current schema
            "updated_at": datetime.now(UTC).isoformat(),
        }
        db.update_lead(phone, update_payload)

        # 5. Sync to Google Sheets (Operational Visibility)
        try:
            # Lazy import to avoid circular dependency
            from config.container import container

            # Prepare flattened data for sync
            pref_zones = state["preferences"].zones if state.get("preferences") else []

            # Get message count from lead data (messages were already persisted)
            message_count = len(lead.get("messages", [])) + 2  # +2 for the new user and AI messages

            sync_data = {
                "phone": phone,
                "name": lead.get("customer_name"),
                "status": lead.get("journey_state") or lead.get("status"),
                "intent": state.get("intent"),
                "budget": state.get("budget"),
                "zones": pref_zones,
                "message_count": message_count,
            }
            container.sheets.sync_lead(sync_data)
        except Exception as e:
            # Don't fail the flow for sheet sync
            logger.warning("SHEET_SYNC_TRIGGER_FAILED", context={"error": str(e)})

        return {"checkpoint": "done"}

    # Define Graph
    workflow = StateGraph(AgentState)

    workflow.add_node("ingest", ingest_node)
    workflow.add_node("fifi_appraisal", fifi_appraisal_node)
    workflow.add_node("intent", intent_node)
    workflow.add_node("lead_qual", lead_qualification_node)
    workflow.add_node("preferences", preference_extraction_node)
    workflow.add_node("sentiment", sentiment_analysis_node)
    workflow.add_node("market_analysis", market_analysis_node)
    workflow.add_node("cache_check", cache_check_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("generation", generation_node)
    workflow.add_node("finalize", finalize_node)
    workflow.add_node("handoff", handoff_node)

    workflow.add_edge(START, "ingest")

    def route_after_ingest(state: AgentState) -> str:
        if state["checkpoint"] == "human_mode":
            return str(END)
        if state["source"] == "FIFI_APPRAISAL":
            return "fifi_appraisal"
        # If in Qualification Mode, route to it
        status = state["lead_data"].get("journey_state")
        if status == LeadStatus.QUALIFICATION_IN_PROGRESS:
            return "lead_qual"
        return "intent"

    workflow.add_conditional_edges("ingest", route_after_ingest)

    def route_after_fifi(state: AgentState) -> str:
        fifi_data = state.get("fifi_data", {})
        if fifi_data.get("fifi_status") == "HUMAN_REVIEW_REQUIRED":
            return "handoff"
        return "intent"

    workflow.add_conditional_edges("fifi_appraisal", route_after_fifi)

    # Intent -> Check if we switched to Qual
    def route_after_intent(state: AgentState) -> str:
        status = state["lead_data"].get("journey_state")
        if status == LeadStatus.QUALIFICATION_IN_PROGRESS:
            return "lead_qual"
        return "preferences"

    workflow.add_conditional_edges("intent", route_after_intent)
    workflow.add_edge("lead_qual", "finalize")
    workflow.add_edge("preferences", "sentiment")

    def route_after_sentiment(state: AgentState) -> str:
        # Trigger Handoff if user is ANGRY or explicitly asking for human
        if state["sentiment"].sentiment == "ANGRY":
            return "handoff"
        # Simple keyword check backup
        if "human" in state["user_input"].lower() or "agent" in state["user_input"].lower():
            return "handoff"
        return "market_analysis"

    workflow.add_conditional_edges("sentiment", route_after_sentiment)
    workflow.add_edge("market_analysis", "cache_check")

    # Conditional edge from cache_check
    def route_after_cache(state: AgentState) -> Literal["finalize", "retrieval"]:
        if state["checkpoint"] == "cache_hit":
            return "finalize"
        return "retrieval"

    workflow.add_edge("handoff", "finalize")

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
        price = p.get("price") or p.get("sale_price_eur") or 0
        res += f"- {p.get('title', 'Property')}: €{int(price):,}\n"
    return res


def _extract_qualification_field(field: str, text: str, api_key: SecretStr, model: str) -> Any:  # noqa: PLR0911, PLR0912
    """Helper to extract specific fields for lead qualification."""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_mistralai import ChatMistralAI

    from domain.qualification import FinancingStatus, Intent, Timeline

    if field == "budget":
        return _extract_budget(text)

    # Generic extraction using LLM for Enums and other fields
    llm = ChatMistralAI(api_key=api_key, model_name=model)

    system_prompt = (
        f"You are a data extraction assistant. Extract the value for the field '{field}' from the user text.\n"
        "Return ONLY the extracted value. If strictly matching an Enum, return the Enum value.\n"
    )

    if field == "intent":
        system_prompt += (
            "Possible values: 'buy', 'sell', 'rent', 'info'.\n"
            "Example: 'voglio comprare' -> 'buy'. 'cerco casa' -> 'buy'. 'voglio vendere' -> 'sell'."
        )
    elif field == "timeline":
        system_prompt += (
            "Possible values: 'urgent' (<30 days), 'medium' (2-3 months), 'long' (>6 months).\n"
            "Example: 'subito' -> 'urgent'. 'entro l'anno' -> 'long'."
        )
    elif field == "financing":
        system_prompt += (
            "Possible values: 'approved' (yes/approved), 'processing' (in progress), 'todo' (no/will do).\n"
            "Example: 'ho i soldi' -> 'approved'. 'devo chiedere' -> 'todo'."
        )
    elif (
        field == "location_specific" or field == "property_specific" or field == "contact_complete"
    ):
        system_prompt += "Return 'True' if the user provided specific details, 'False' if generally open or vague."

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{text}"),
        ]
    )

    try:
        result = llm.invoke(prompt.format(text=text)).content
        clean_result = str(result).lower().strip().replace("'", "").replace('"', "")

        # Mapping back to Enums
        if field == "intent":
            if "buy" in clean_result:
                return Intent.BUY
            if "sell" in clean_result:
                return Intent.SELL
            if "rent" in clean_result:
                return Intent.RENT
            if "info" in clean_result:
                return Intent.INFO
            return Intent.UNKNOWN
        elif field == "timeline":
            if "urgent" in clean_result:
                return Timeline.URGENT
            if "medium" in clean_result:
                return Timeline.MEDIUM
            if "long" in clean_result:
                return Timeline.LONG
            return Timeline.UNKNOWN
        elif field == "financing":
            if "approved" in clean_result:
                return FinancingStatus.APPROVED
            if "process" in clean_result:
                return FinancingStatus.PROCESSING
            if "todo" in clean_result:
                return FinancingStatus.TODO
            return FinancingStatus.UNKNOWN
        elif field in ["location_specific", "property_specific", "contact_complete"]:
            return "true" in clean_result

        return clean_result
    except Exception as e:
        logger.error("QUALIFICATION_EXTRACTION_FAILED", context={"error": str(e)})
        return None
