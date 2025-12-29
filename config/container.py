from typing import Any

from application.services.journey_manager import JourneyManager
from application.services.lead_processor import LeadProcessor, LeadScorer
from config.settings import settings
from domain.ports import MessagingPort
from infrastructure.adapters.calcom_adapter import CalComAdapter
from infrastructure.adapters.document_adapter import DocumentAdapter
from infrastructure.adapters.langchain_adapter import LangChainAdapter
from infrastructure.adapters.market_adapter import IdealistaMarketAdapter
from infrastructure.adapters.meta_whatsapp_adapter import MetaWhatsAppAdapter
from infrastructure.adapters.scraper_adapter import ImmobiliareScraperAdapter
from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.adapters.twilio_adapter import TwilioAdapter


class Container:
    def __init__(self) -> None:
        # Infrastructure Adapters
        self.db: SupabaseAdapter = SupabaseAdapter()
        self.ai: LangChainAdapter = LangChainAdapter()
        self.msg: MessagingPort
        if settings.WHATSAPP_PROVIDER == "meta":
            self.msg = MetaWhatsAppAdapter()
        else:
            self.msg = TwilioAdapter()
        self.calendar: CalComAdapter = CalComAdapter()
        self.doc_gen: DocumentAdapter = DocumentAdapter()
        self.scraper: ImmobiliareScraperAdapter = ImmobiliareScraperAdapter()
        self.market: IdealistaMarketAdapter = IdealistaMarketAdapter()

        # Lazy loaded sheets adapter
        self._sheets: Any | None = None

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
            calendar=self.calendar,
        )

    @property
    def sheets(self) -> Any:
        """Lazy load Google Sheets adapter."""
        if not self._sheets:
            from infrastructure.adapters.google_sheets_adapter import GoogleSheetsAdapter

            self._sheets = GoogleSheetsAdapter()
        return self._sheets


# Composition Root Instance
container = Container()
