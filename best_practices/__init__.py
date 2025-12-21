"""
GEMINI Best Practices Registry
Central repository for approved engineering patterns.
"""

CODE_PATTERNS = {
    "CIRCUIT_BREAKER": {
        "id": "RESILIENCE_CB_001",
        "name": "External Service Circuit Breaker",
        "description": "All external API calls (Twilio, Mistral, Supabase) must be wrapped in a retry/circuit-breaker logic using `tenacity`.",
        "snippet": "@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))",
    },
    "STRUCTURED_LOGGING": {
        "id": "OBSERVABILITY_LOG_001",
        "name": "Structured JSON Logging",
        "description": "Logs must be structured with context dictionaries, not f-strings.",
        "snippet": "logger.info('EVENT_NAME', context={'key': 'value'})",
    },
    "ADR_DOCUMENTATION": {
        "id": "DOCS_ADR_001",
        "name": "Architectural Decision Records",
        "description": "Significant architectural changes must be documented in `docs/adr/`.",
    },
    "HEXAGONAL_LAYERS": {
        "id": "ARCH_HEX_001",
        "name": "Strict Layer Boundaries",
        "description": "Domain layer must not import from Infrastructure or Presentation layers.",
    }
}
