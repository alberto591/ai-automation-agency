from typing import Any, Literal

from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from application.services.scoring import ScoringService
from config.settings import settings
from domain.qualification import Intent, QualificationData, Timeline


# Define the state of the qualification conversation
class QualificationState(TypedDict):
    phone: str
    step: Literal[
        "intent",
        "timeline",
        "budget",
        "financing",
        "location",
        "property_type",
        "contact",
        "complete",
    ]
    data: dict[str, Any]
    next_message: str | None
    is_complete: bool


def get_next_step(current_step: str) -> str:
    steps = [
        "intent",
        "timeline",
        "budget",
        "financing",
        "location",
        "property_type",
        "contact",
        "complete",
    ]
    try:
        idx = steps.index(current_step)
        return steps[idx + 1]
    except (ValueError, IndexError):
        return "complete"


# --- Nodes ---


def ask_question_node(state: QualificationState) -> QualificationState:
    """Determines the next question based on current step."""
    step = state["step"]
    msg = ""

    if step == "intent":
        msg = "Ciao! 👋 Sono qui per aiutarti a trovare la casa perfetta. Cerchi di comprare, vendere, o solo informarti?"
    elif step == "timeline":
        msg = "Ottimo! Quando hai bisogno della casa? (Entro 30 giorni, 2-3 mesi, o più avanti?)"
    elif step == "budget":
        msg = "Qual è il tuo budget indicativo per l'acquisto?"
    elif step == "financing":
        msg = "Hai già un mutuo approvato o devi ancora fare richiesta?"
    elif step == "location":
        msg = "In quale zona preferiresti cercare? (es. Firenze Centro, periferia...)"
    elif step == "property_type":
        msg = "Che tipo di proprietà cerchi? (Appartamento, Villa, etc.)"
    elif step == "contact":
        msg = "Ultimo step: come posso chiamarti? (Nome e Cognome)"

    return {
        "next_message": msg,
        "is_complete": False,
        "phone": state["phone"],
        "step": state["step"],
        "data": state["data"],
    }


def process_answer_node(state: QualificationState) -> QualificationState:
    """
    Parses the user's last message and updates state.
    In a real implementation, this would use an LLM to extract structured data.
    For this prototype, we'll assume the extraction happens before or we simulate it.
    """
    # NOTE: This node is a placeholder. In the full graph, we'd have an LLM call here
    # to extract entity -> update state.data -> determine next step.

    current_step = state["step"]
    next_step = get_next_step(current_step)

    return {
        "step": next_step,  # type: ignore
        "next_message": None,
        "is_complete": next_step == "complete",
        "phone": state["phone"],
        "data": state["data"],
    }


def score_lead_node(state: QualificationState) -> QualificationState:
    """Final node: calculates score and categorizes lead."""
    # Convert dict to domain model
    q_data = QualificationData(
        intent=state["data"].get("intent", Intent.UNKNOWN),
        timeline=state["data"].get("timeline", Timeline.UNKNOWN),
        # ... map other fields ...
        has_contact_info=True,  # Since we are chatting
    )

    score = ScoringService.calculate_score(q_data)

    # Generate final message based on category
    if score.category == "HOT":
        final_msg = (
            "✅ Grazie! Sei un profilo priorità HOT. Un nostro agente ti chiamerà tra 5 minuti.\n"
            f"Oppure prenota subito una chiamata prioritaria qui: {settings.CALCOM_BOOKING_LINK}"
        )
    else:
        final_msg = "Grazie! Ti manderemo aggiornamenti via email."

    return {
        "next_message": final_msg,
        "is_complete": True,
        "step": "complete",
        "phone": state["phone"],
        "data": state["data"],
    }


# --- Graph ---


def create_qualification_graph() -> Any:
    workflow = StateGraph(QualificationState)

    workflow.add_node("ask", ask_question_node)
    workflow.add_node("process", process_answer_node)
    workflow.add_node("score", score_lead_node)

    workflow.set_entry_point("ask")

    # Edges
    # After asking, we wait for user input (in a real chatbot this would pause)
    # Here we define the logical flow assuming we get input:
    # Ask -> Process -> (Check if complete) -> Ask/Score

    # Conditional edge logic would go here.
    # For now, simplest linear flow definition:
    workflow.add_edge("ask", "process")

    # Conditional from process
    def check_completion(state: QualificationState) -> str:
        if state["step"] == "complete":
            return "score"
        return "ask"

    workflow.add_conditional_edges("process", check_completion, {"score": "score", "ask": "ask"})

    workflow.add_edge("score", END)

    return workflow.compile()
