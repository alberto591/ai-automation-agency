"""
Anzevino AI Best Practices Registry

Central repository for approved engineering patterns specific to the
AI Real Estate Agent project.
"""

from typing import Any

CODE_PATTERNS = {
    # Resilience Patterns
    "CIRCUIT_BREAKER": {
        "id": "RESILIENCE_CB_001",
        "name": "External Service Circuit Breaker",
        "description": "All external API calls (Twilio, Mistral, Supabase) must be wrapped in retry/circuit-breaker logic using `tenacity`.",
        "snippet": "@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))",
        "tags": ["resilience", "external-api"],
    },
    # Observability Patterns
    "STRUCTURED_LOGGING": {
        "id": "OBSERVABILITY_LOG_001",
        "name": "Structured JSON Logging",
        "description": "Logs must be structured with context dictionaries, not f-strings.",
        "snippet": "logger.info('EVENT_NAME', context={'key': 'value'})",
        "tags": ["observability", "logging"],
    },
    # Documentation Patterns
    "ADR_DOCUMENTATION": {
        "id": "DOCS_ADR_001",
        "name": "Architectural Decision Records",
        "description": "Significant architectural changes must be documented in `docs/adr/`.",
        "tags": ["documentation", "architecture"],
    },
    # Architecture Patterns
    "HEXAGONAL_LAYERS": {
        "id": "ARCH_HEX_001",
        "name": "Strict Layer Boundaries",
        "description": "Domain layer must not import from Infrastructure or Presentation layers.",
        "tags": ["architecture", "hexagonal"],
    },
    # Lead & Compliance Patterns (Real Estate specific)
    "LEAD_QUALIFICATION": {
        "id": "LEAD_QUAL_001",
        "name": "AI-Driven Lead Scoring",
        "description": "Use LLM reasoning for lead qualification, never keyword lists or hardcoded rules.",
        "snippet": "await ai_adapter.classify_lead(conversation_history)",
        "tags": ["lead", "ai-reasoning", "compliance"],
    },
    "APPRAISAL_DISCLAIMER": {
        "id": "LEGAL_DISC_001",
        "name": "Appraisal Disclaimer Requirement",
        "description": "All property valuations must include legal disclaimer that values are estimates only.",
        "snippet": "DISCLAIMER = 'This valuation is an automated estimate and should not replace a professional appraisal.'",
        "tags": ["legal", "appraisal", "compliance"],
    },
    "PROPERTY_VALUATION_AUDIT": {
        "id": "AVM_AUDIT_001",
        "name": "AVM Audit Trail",
        "description": "All automated property valuations must be logged with full input/output for audit purposes.",
        "snippet": "await audit_log.record_valuation(property_id, inputs, output, model_version)",
        "tags": ["avm", "audit", "compliance"],
    },
    # WhatsApp Integration Patterns
    "WHATSAPP_MESSAGE_HANDLING": {
        "id": "WHATSAPP_MSG_001",
        "name": "Twilio WhatsApp Message Handler",
        "description": "All WhatsApp messages must be processed through the Twilio adapter with proper validation.",
        "tags": ["whatsapp", "twilio", "messaging"],
    },
    # Embedding Patterns
    "EMBEDDING_1024D_MISTRAL": {
        "id": "EMBED_MISTRAL_001",
        "name": "Mistral 1024D Embedding Standard",
        "description": "All embeddings must use Mistral's mistral-embed model (1024 dimensions).",
        "snippet": "response = client.embeddings.create(model='mistral-embed', inputs=[text])",
        "tags": ["embedding", "mistral", "rag"],
    },
    # Portal Sync Patterns
    "PORTAL_SYNC": {
        "id": "PORTAL_SYNC_001",
        "name": "Multi-Portal Property Sync",
        "description": "Property listings must be synchronized across all configured portals with conflict resolution.",
        "tags": ["portal", "sync", "property"],
    },
}


def get_pattern_ids() -> list[str]:
    """Get all pattern IDs."""
    return list(CODE_PATTERNS.keys())


def get_patterns(
    tags: list[str] | None = None, severity: str | None = None
) -> dict[str, dict[str, Any]]:
    """Get patterns filtered by tags and/or severity."""
    patterns = CODE_PATTERNS.copy()
    if tags:
        patterns = {
            k: v for k, v in patterns.items() if any(tag in v.get("tags", []) for tag in tags)
        }
    return patterns


def get_patterns_for_file(filepath: str) -> dict[str, dict[str, Any]]:
    """Get relevant patterns based on file path."""
    patterns = {}

    if "infrastructure" in filepath:
        patterns.update(
            {k: v for k, v in CODE_PATTERNS.items() if "external-api" in v.get("tags", [])}
        )
    if "domain" in filepath:
        patterns["HEXAGONAL_LAYERS"] = CODE_PATTERNS["HEXAGONAL_LAYERS"]
    if "adapters" in filepath and "twilio" in filepath.lower():
        patterns["WHATSAPP_MESSAGE_HANDLING"] = CODE_PATTERNS["WHATSAPP_MESSAGE_HANDLING"]
    if "avm" in filepath.lower() or "appraisal" in filepath.lower():
        patterns["PROPERTY_VALUATION_AUDIT"] = CODE_PATTERNS["PROPERTY_VALUATION_AUDIT"]
        patterns["APPRAISAL_DISCLAIMER"] = CODE_PATTERNS["APPRAISAL_DISCLAIMER"]

    return patterns


def get_gotchas_for_file(filepath: str) -> list[str]:
    """Get common gotchas for a file based on its path."""
    gotchas = []

    if "infrastructure" in filepath:
        gotchas.append("Ensure all external API calls have circuit breaker wrapping")
        gotchas.append("Never block async event loop with sync calls")
    if "domain" in filepath:
        gotchas.append("Domain layer must not import from infrastructure or presentation")
        gotchas.append("Keep domain logic pure - no I/O operations")
    if "presentation" in filepath:
        gotchas.append("Validate all user input with Pydantic before processing")
    if "avm" in filepath.lower():
        gotchas.append("All valuations must include legal disclaimer")
        gotchas.append("Log full audit trail for regulatory compliance")

    return gotchas
