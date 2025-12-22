from application.services.lead_processor import LeadProcessor, LeadScorer
from application.services.journey_manager import JourneyManager
from infrastructure.adapters.langchain_adapter import LangChainAdapter
from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.adapters.twilio_adapter import TwilioAdapter
from infrastructure.adapters.google_calendar_adapter import GoogleCalendarAdapter
from infrastructure.adapters.document_adapter import DocumentAdapter
from infrastructure.adapters.scraper_adapter import ImmobiliareScraperAdapter


class Container:
    def __init__(self) -> None:
        # Infrastructure Adapters
        self.db: SupabaseAdapter = SupabaseAdapter()
        self.ai: LangChainAdapter = LangChainAdapter()
        self.msg: TwilioAdapter = TwilioAdapter()
        self.calendar: GoogleCalendarAdapter = GoogleCalendarAdapter()
        self.doc_gen: DocumentAdapter = DocumentAdapter()
        self.scraper: ImmobiliareScraperAdapter = ImmobiliareScraperAdapter()

        # Domain/Application Services
        self.journey: JourneyManager = JourneyManager(
            db=self.db, 
            calendar=self.calendar, 
            doc_gen=self.doc_gen, 
            msg=self.msg
        )
        self.scorer: LeadScorer = LeadScorer()
        self.lead_processor: LeadProcessor = LeadProcessor(
            db=self.db, 
            ai=self.ai, 
            msg=self.msg, 
            scorer=self.scorer,
            journey=self.journey,
            scraper=self.scraper
        )


# Composition Root Instance
container = Container()
