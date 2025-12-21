from application.services.lead_processor import LeadProcessor, LeadScorer
from infrastructure.adapters.mistral_adapter import MistralAdapter
from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.adapters.twilio_adapter import TwilioAdapter


class Container:
    def __init__(self) -> None:
        # Infrastructure Adapters (Singleton-like in this instance)
        self.db: SupabaseAdapter = SupabaseAdapter()
        self.ai: MistralAdapter = MistralAdapter()
        self.msg: TwilioAdapter = TwilioAdapter()

        # Domain/Application Services
        self.scorer: LeadScorer = LeadScorer()
        self.lead_processor: LeadProcessor = LeadProcessor(
            db=self.db, ai=self.ai, msg=self.msg, scorer=self.scorer
        )


# Composition Root Instance
container = Container()
