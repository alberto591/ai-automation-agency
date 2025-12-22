from application.services.journey_manager import JourneyManager
from application.services.lead_processor import LeadProcessor, LeadScorer
from infrastructure.adapters.document_adapter import DocumentAdapter
from infrastructure.adapters.google_calendar_adapter import GoogleCalendarAdapter
from infrastructure.adapters.langchain_adapter import LangChainAdapter
from infrastructure.adapters.market_adapter import IdealistaMarketAdapter
from infrastructure.adapters.scraper_adapter import ImmobiliareScraperAdapter
from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.adapters.twilio_adapter import TwilioAdapter


class Container:
    def __init__(self) -> None:
        # Infrastructure Adapters
        self.db: SupabaseAdapter = SupabaseAdapter()
        self.ai: LangChainAdapter = LangChainAdapter()
        self.msg: TwilioAdapter = TwilioAdapter()
        self.calendar: GoogleCalendarAdapter = GoogleCalendarAdapter()
        self.doc_gen: DocumentAdapter = DocumentAdapter()
        self.scraper: ImmobiliareScraperAdapter = ImmobiliareScraperAdapter()
        self.market: IdealistaMarketAdapter = IdealistaMarketAdapter()

        # Domain/Application Services
        self.journey: JourneyManager = JourneyManager(
            db=self.db, calendar=self.calendar, doc_gen=self.doc_gen, msg=self.msg
        )
        self.scorer: LeadScorer = LeadScorer()
        self.lead_processor: LeadProcessor = LeadProcessor(
            db=self.db,
            ai=self.ai,
            msg=self.msg,
            scorer=self.scorer,
            journey=self.journey,
            scraper=self.scraper,
            market=self.market,
        )


# Composition Root Instance
container = Container()
