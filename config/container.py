from typing import TYPE_CHECKING, Any

from application.services.appraisal import AppraisalService
from application.services.journey_manager import JourneyManager
from application.services.lead_ingestion_service import LeadIngestionService
from application.services.lead_processor import LeadProcessor, LeadScorer
from application.services.market_intelligence import MarketIntelligenceService
from application.services.payment_service import PaymentService
from application.services.routing_service import RoutingService
from config.settings import settings
from domain.ports import CachePort, CalendarPort, MessagingPort

if TYPE_CHECKING:
    pass


class Container:
    def __init__(self) -> None:
        # Import Adapters lazily to avoid circular imports with config
        from infrastructure.adapters.cache_adapter import (  # noqa: PLC0415
            InMemoryCacheAdapter,
            RedisAdapter,
        )
        from infrastructure.adapters.calcom_adapter import CalComAdapter  # noqa: PLC0415
        from infrastructure.adapters.document_adapter import DocumentAdapter  # noqa: PLC0415
        from infrastructure.adapters.langchain_adapter import LangChainAdapter  # noqa: PLC0415
        from infrastructure.adapters.market_adapter import IdealistaMarketAdapter  # noqa: PLC0415
        from infrastructure.adapters.meta_whatsapp_adapter import (  # noqa: PLC0415
            MetaWhatsAppAdapter,
        )
        from infrastructure.adapters.scraper_adapter import (  # noqa: PLC0415
            ImmobiliareScraperAdapter,
        )
        from infrastructure.adapters.supabase_adapter import SupabaseAdapter  # noqa: PLC0415
        from infrastructure.adapters.twilio_adapter import TwilioAdapter  # noqa: PLC0415

        # Infrastructure Adapters
        self.db: SupabaseAdapter = SupabaseAdapter()
        self.ai: LangChainAdapter = LangChainAdapter()
        self.msg: MessagingPort
        if settings.WHATSAPP_PROVIDER == "meta":
            self.msg = MetaWhatsAppAdapter()
        else:
            self.msg = TwilioAdapter()
        self.calendar: CalendarPort = CalComAdapter()
        self.doc_gen: DocumentAdapter = DocumentAdapter()
        self.scraper: ImmobiliareScraperAdapter = ImmobiliareScraperAdapter()
        self.market: IdealistaMarketAdapter = IdealistaMarketAdapter()

        # Cache initialization
        cache: CachePort
        if settings.REDIS_URL:
            cache = RedisAdapter(settings.REDIS_URL)
        else:
            cache = InMemoryCacheAdapter()
        self.cache = cache

        self.market_intel: MarketIntelligenceService = MarketIntelligenceService(
            db=self.db, ai=self.ai, cache=self.cache
        )

        # Lazy loaded sheets adapter
        self._sheets: Any | None = None

        # Domain/Application Services
        self.journey: JourneyManager = JourneyManager(
            db=self.db, calendar=self.calendar, doc_gen=self.doc_gen, msg=self.msg
        )

        self.payment_service: PaymentService = PaymentService(db=self.db, msg=self.msg)
        self.routing_service: RoutingService = RoutingService(db=self.db)

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
            email=self.email,
            validation=self.validation,
            routing=self.routing_service,
        )

        # Local property search (for performance optimization)
        from application.services.local_property_search import LocalPropertySearchService
        from infrastructure.monitoring.performance_logger import PerformanceMetricLogger

        # Use the Supabase client from the SupabaseAdapter
        self.local_property_search = LocalPropertySearchService(db_client=self.db.client)
        self.performance_logger = PerformanceMetricLogger(db_client=self.db.client)

        self.appraisal_service: AppraisalService = AppraisalService(
            research_port=self.research,
            local_search=self.local_property_search,
            performance_logger=self.performance_logger,
        )

        # Stripe Connect (lazy loaded)
        self._stripe_connect: Any | None = None

    @property
    def stripe_connect(self) -> Any:
        """Lazy load Stripe Connect adapter."""
        if not self._stripe_connect:
            from infrastructure.adapters.stripe_connect_adapter import (  # noqa: PLC0415
                StripeConnectAdapter,
            )

            self._stripe_connect = StripeConnectAdapter()
        return self._stripe_connect

    @property
    def lead_ingestion(self) -> LeadIngestionService:
        return LeadIngestionService(lead_processor=self.lead_processor)

    @property
    def sheets(self) -> Any:
        """Lazy load Google Sheets adapter."""
        if not self._sheets:
            from infrastructure.adapters.google_sheets_adapter import (  # noqa: PLC0415
                GoogleSheetsAdapter,
            )

            self._sheets = GoogleSheetsAdapter()
        return self._sheets

    @property
    def voice(self) -> Any:
        """Lazy load Voice adapter."""
        from infrastructure.adapters.voice_adapter import (  # noqa: PLC0415
            TwilioVoiceAdapter,
        )

        return TwilioVoiceAdapter()

    @property
    def email_ingestion(self) -> Any:
        """Lazy load Email service."""
        from application.services.email_parser import (  # noqa: PLC0415
            EmailParserService,
        )

        # noqa: PLC0415
        from infrastructure.adapters.imap_adapter import IMAPAdapter  # noqa: PLC0415

        adapter = IMAPAdapter()
        return EmailParserService(email_port=adapter)

    @property
    def research(self) -> Any:
        """Lazy load Research adapter (Perplexity Labs) with Redis cache."""
        from infrastructure.adapters.perplexity_adapter import (  # noqa: PLC0415
            PerplexityAdapter,
        )
        from infrastructure.cache import RedisPerplexityCache  # noqa: PLC0415

        cache = RedisPerplexityCache(redis_url=settings.REDIS_URL, ttl_hours=24)
        return PerplexityAdapter(cache=cache)

    @property
    def validation(self) -> Any:
        """Lazy load Validation adapter (Postgres/Supabase)."""
        from infrastructure.adapters.validation_adapter import (  # noqa: PLC0415
            PostgresValidationAdapter,
        )

        return PostgresValidationAdapter()

    @property
    def email(self) -> Any:
        """Lazy load Email adapter (IMAP)."""
        from infrastructure.adapters.imap_adapter import IMAPAdapter  # noqa: PLC0415

        return IMAPAdapter()


# Composition Root Instance
container = Container()
