import os
import re
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, cast
from uuid import UUID

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    Form,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
)
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, Field

from application.services.lead_scorer import LeadScorer
from application.services.scoring import ScoringService
from config.container import container
from config.settings import settings
from domain.appraisal import AppraisalRequest, AppraisalResult
from domain.enums import LeadStatus
from domain.errors import BaseAppError
from domain.qualification import LeadCategory, LeadScore, QualificationData
from infrastructure.logging import get_logger
from infrastructure.monitoring.sentry import init_sentry
from presentation.api import feedback
from presentation.api.webhooks import calcom_webhook, portal_webhook, voice_webhook
from presentation.middleware.auth import get_current_user

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    # Startup
    logger.info("API_STARTUP")

    # Initialize Sentry
    if settings.SENTRY_DSN:
        init_sentry(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            traces_sample_rate=1.0 if settings.ENVIRONMENT == "development" else 0.1,
        )
        logger.info("SENTRY_ENABLED", context={"environment": settings.ENVIRONMENT})
    else:
        logger.warning("SENTRY_DISABLED", context={"reason": "No DSN configured"})

    # Background task for email polling
    import asyncio

    async def poll_emails() -> None:
        while True:
            try:
                # Poll every 5 minutes
                await asyncio.sleep(300)
                # Skip polling if no email configured
                if not settings.IMAP_PASSWORD:
                    continue

                logger.info("POLLING_EMAILS")
                count = container.lead_processor.process_new_emails()
                if count > 0:
                    logger.info("EMAILS_PROCESSED", context={"count": count})
            except Exception as e:
                logger.error("EMAIL_POLL_LOOP_ERROR", context={"error": str(e)})
                await asyncio.sleep(60)  # Backoff on error

    # Start polling
    polling_task = asyncio.create_task(poll_emails())

    yield

    # Shutdown
    polling_task.cancel()
    logger.info("API_SHUTDOWN")


app: FastAPI = FastAPI(
    title="Agenzia AI API",
    lifespan=lifespan,
)

# Middleware / Security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(calcom_webhook.router, prefix="/api")
app.include_router(portal_webhook.router, prefix="/api")
app.include_router(voice_webhook.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")


async def verify_webhook_key(x_webhook_key: str = Header(None)) -> None:
    if settings.WEBHOOK_API_KEY and x_webhook_key != settings.WEBHOOK_API_KEY:
        logger.warning("UNAUTHORIZED_WEBHOOK_ATTEMPT", context={"key": x_webhook_key})
        raise HTTPException(status_code=401, detail="Unauthorized") from None


# DTOs
class LeadRequest(BaseModel):
    name: str = Field(..., min_length=1)
    agency: str
    phone: str
    postcode: str | None = None
    properties: str | None = None


class PhoneRequest(BaseModel):
    phone: str


class ManualMessageRequest(BaseModel):
    phone: str
    message: str


class OutreachGenerateRequest(BaseModel):
    city: str = Field(default="Milano")


class OutreachSendRequest(BaseModel):
    target_id: str


class SalesReportRequest(BaseModel):
    property_id: str
    owner_phone: str | None = None


# --- PUBLIC ENDPOINTS (Webhooks & Lead Ingestion) ---


@app.post("/api/leads")
async def create_lead(lead: LeadRequest) -> dict[str, Any]:
    logger.info("RECEIVED_LEAD_REQUEST", context={"name": lead.name, "phone": lead.phone})

    # Simple validation
    if not re.match(r"^\+[1-9]\d{6,14}$", lead.phone.replace(" ", "")):
        raise HTTPException(status_code=400, detail="Invalid phone format")

    try:
        result = container.lead_processor.process_lead(
            phone=lead.phone,
            name=lead.name,
            query=f"Agency: {lead.agency}. Notes: {lead.properties}",
            postcode=lead.postcode,
        )
        return {"status": "success", "ai_response": result}
    except BaseAppError as e:
        logger.error("API_LEAD_PROCESSING_FAILED", context={"error": e.message, "cause": e.cause})
        raise HTTPException(status_code=500, detail=e.message) from e
    except Exception:
        logger.error("INTERNAL_SERVER_ERROR", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error") from None


class AppraisalPDFRequest(BaseModel):
    address: str
    fifi_data: dict[str, Any]


@app.post("/api/appraisals/generate-pdf")
async def generate_appraisal_pdf(request: AppraisalPDFRequest) -> dict[str, Any]:
    """
    Generate a PDF appraisal report with investment metrics.
    """
    try:
        from infrastructure.ai_pdf_generator import PropertyPDFGenerator  # noqa: PLC0415

        # Prepare appraisal data for PDF
        appraisal_data = {
            "address": request.address,
            "predicted_value": request.fifi_data.get("predicted_value", 0),
            "confidence_range": request.fifi_data.get("confidence_range", "N/A"),
            "confidence_level": request.fifi_data.get("confidence_level", 0),
            "features": request.fifi_data.get("features", {}),
            "investment_metrics": request.fifi_data.get("investment_metrics", {}),
            "comparables": request.fifi_data.get("comparables", []),
        }

        # Generate PDF
        generator = PropertyPDFGenerator()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"appraisal_{timestamp}.pdf"
        output_path = f"temp/documents/{filename}"

        pdf_path = generator.generate_appraisal_report(appraisal_data, output_path)

        logger.info("PDF_GENERATED", context={"path": pdf_path, "address": request.address})

        # For now, return local path (in production, upload to Supabase Storage)
        return {
            "status": "success",
            "pdf_path": pdf_path,
            "filename": filename,
            "message": "PDF generato con successo",
        }

    except Exception as e:
        logger.error("PDF_GENERATION_FAILED", context={"error": str(e)}, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate PDF") from e


@app.post("/api/webhooks/twilio")
async def twilio_webhook(
    background_tasks: BackgroundTasks,
    request: Request,
) -> str:
    """
    Receives webhooks from Twilio for incoming WhatsApp messages and media.
    """
    form_data = await request.form()
    # Cast to str to satisfy mypy since form_data can contain UploadFile
    from_phone = str(form_data.get("From", ""))
    body = str(form_data.get("Body", ""))
    num_media_val = form_data.get("NumMedia", 0)
    num_media = int(str(num_media_val)) if num_media_val is not None else 0

    media_url_val = form_data.get("MediaUrl0")
    media_url = str(media_url_val) if num_media > 0 and media_url_val else None

    logger.info("WEBHOOK_RECEIVED", context={"from": from_phone, "body": body, "media": media_url})

    # Process in background
    background_tasks.add_task(
        container.lead_processor.process_incoming_message,
        phone=from_phone,
        text=body,
        media_url=media_url,
    )

    return "OK"


@app.post("/api/webhooks/twilio/status")
async def twilio_status_callback(
    MessageSid: str = Form(...),  # noqa: N803
    MessageStatus: str = Form(...),  # noqa: N803
) -> str:
    """
    Receives delivery and read receipts from Twilio.
    """
    logger.info("TWILIO_STATUS_UPDATE", context={"sid": MessageSid, "status": MessageStatus})
    try:
        container.db.update_message_status(sid=MessageSid, status=MessageStatus)
    except Exception as e:
        logger.error("STATUS_UPDATE_FAILED", context={"sid": MessageSid, "error": str(e)})

    return "OK"


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "anzevino-ai-api"}


@app.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# --- PROTECTED ENDPOINTS (Dashboard Actions) ---


@app.post("/api/leads/takeover", dependencies=[Depends(get_current_user)])
async def takeover_lead(req: PhoneRequest) -> dict[str, str]:
    try:
        container.lead_processor.takeover(req.phone)
        return {"status": "success", "message": "AI Muted. Human in control."}
    except Exception as e:
        logger.error("TAKEOVER_FAILED", context={"phone": req.phone, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to mute AI") from None


@app.post("/api/leads/resume", dependencies=[Depends(get_current_user)])
async def resume_lead(req: PhoneRequest) -> dict[str, str]:
    try:
        container.lead_processor.resume(req.phone)
        return {"status": "success", "message": "AI Resumed."}
    except Exception as e:
        logger.error("RESUME_FAILED", context={"phone": req.phone, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to resume AI") from None


@app.post("/api/leads/message", dependencies=[Depends(get_current_user)])
async def send_manual_message(
    req: ManualMessageRequest, background_tasks: BackgroundTasks
) -> dict[str, str]:
    try:
        # 1. Send message immediately
        sid = container.lead_processor.send_manual_message(
            req.phone, req.message, skip_history=True
        )

        # 2. Schedule history update in background
        background_tasks.add_task(
            container.lead_processor.add_message_history,
            req.phone,
            "assistant",
            req.message,
            sid=sid,
            status="sent",
            metadata={"by": "human_agent"},
        )

        return {"status": "success", "message": "Message queued.", "sid": sid}
    except Exception as e:
        logger.error("MANUAL_MESSAGE_FAILED", context={"phone": req.phone, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to send message") from None


class LeadUpdate(BaseModel):
    phone: str
    name: str | None = None
    budget: int | None = None
    zones: list[str] | None = None
    status: str | None = None
    journey_state: str | None = None
    scheduled_at: str | None = None  # Receive as ISO string


@app.patch("/api/leads", dependencies=[Depends(get_current_user)])
async def update_lead(req: LeadUpdate) -> dict[str, str]:
    try:
        # Use lead_processor to update domain record
        container.lead_processor.update_lead_details(
            phone=req.phone,
            name=req.name,
            budget=req.budget,
            zones=req.zones,
            status=req.status,
            journey_state=req.journey_state,
            scheduled_at=req.scheduled_at,
        )
        return {"status": "success", "message": "Lead updated."}
    except Exception as e:
        logger.error("LEAD_UPDATE_FAILED", context={"phone": req.phone, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to update lead") from None


class ScheduleRequest(BaseModel):
    phone: str
    start_time: str  # ISO string


@app.post("/api/leads/schedule", dependencies=[Depends(get_current_user)])
async def schedule_viewing(req: ScheduleRequest) -> dict[str, str]:
    try:
        dt = datetime.fromisoformat(req.start_time.replace("Z", "+00:00"))
        container.journey.transition_to(req.phone, LeadStatus.SCHEDULED, context={"start_time": dt})
        return {"status": "success", "message": "Viewing scheduled."}
    except Exception as e:
        logger.error("SCHEDULE_FAILED", context={"phone": req.phone, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to schedule viewing") from None


class ContractRequest(BaseModel):
    phone: str
    offered_price: int


@app.post("/api/leads/generate-contract", dependencies=[Depends(get_current_user)])
async def generate_contract(req: ContractRequest) -> dict[str, str]:
    try:
        container.journey.transition_to(
            req.phone, LeadStatus.CONTRACT_PENDING, context={"offered_price": req.offered_price}
        )
        return {"status": "success", "message": "Contract generation triggered."}
    except Exception as e:
        logger.error("CONTRACT_GEN_FAILED", context={"phone": req.phone, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to generate contract") from None


@app.get("/api/user/profile", dependencies=[Depends(get_current_user)])
async def get_user_profile() -> dict[str, Any]:
    return {
        "name": (
            settings.AGENCY_OWNER_PHONE.split("@")[0]
            if settings.AGENCY_OWNER_PHONE
            else "Agency Owner"
        ),
        "email": settings.AGENCY_OWNER_EMAIL or "info@anzevino.ai",
        "phone": settings.AGENCY_OWNER_PHONE or "+39 123 456 7890",
        "agency_name": "Anzevino AI",
    }


# --- NEW INTELLIGENCE ENDPOINTS ---


@app.get("/api/leads/{phone}/summary", dependencies=[Depends(get_current_user)])
async def get_lead_summary(phone: str) -> dict[str, Any]:
    """
    Generates an AI summary of the conversation + sentiment analysis.
    """
    try:
        summary_data = container.lead_processor.summarize_lead(phone)
        return summary_data
    except Exception as e:
        logger.error("SUMMARY_ENDPOINT_FAILED", context={"phone": phone, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to generate summary") from None


@app.get("/api/market/valuation", dependencies=[Depends(get_current_user)])
async def get_market_valuation(
    zone: str = Query(..., min_length=2),
    city: str = Query(default=""),
) -> dict[str, Any]:
    """
    Returns market valuation data for a specific zone using the MarketDataPort.
    """
    try:
        insights = container.market.get_market_insights(zone, city)
        return {"status": "success", "data": insights}
    except Exception as e:
        logger.error("MARKET_VALUATION_FAILED", context={"zone": zone, "error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to fetch market data") from None


@app.get("/api/monitoring/performance")
async def get_performance_monitoring(
    hours: int = Query(default=24, ge=1, le=168),
) -> dict[str, Any]:
    """
    Returns aggregated performance statistics for the last N hours.
    Used by the internal monitoring dashboard.
    """
    try:
        # Call the Supabase RPC function
        result = container.db.client.rpc("get_performance_stats", {"p_hours": hours}).execute()

        if not result.data:
            return {
                "total_appraisals": 0,
                "avg_response_ms": 0,
                "p50_response_ms": 0,
                "p90_response_ms": 0,
                "local_hit_rate": 0,
                "avg_confidence": 0,
                "avg_comparables": 0,
            }

        data_list = cast(list[Any], result.data)
        if data_list and len(data_list) > 0:
            return cast(dict[str, Any], data_list[0])
        return {
            "total_appraisals": 0,
            "avg_response_ms": 0,
            "p50_response_ms": 0,
            "p90_response_ms": 0,
            "local_hit_rate": 0,
            "avg_confidence": 0,
            "avg_comparables": 0,
        }

    except Exception as e:
        logger.error("MONITORING_STATS_FAILED", context={"error": str(e)})
        raise HTTPException(
            status_code=500, detail="Failed to fetch monitoring statistics"
        ) from None


@app.post("/api/appraisals/estimate")
async def generate_appraisal(req: AppraisalRequest) -> AppraisalResult:
    """
    Generates an AI-driven property appraisal using real-time market data (Perplexity).
    Public endpoint for Fifi appraisal tool.
    """
    try:
        result = container.appraisal_service.estimate_value(req)

        # Link appraisal to lead if phone is provided
        if req.phone:
            container.lead_processor.process_appraisal_signal(
                phone=req.phone,
                estimated_value=result.estimated_value,
                comparables_count=len(result.comparables),
            )

        return result
    except Exception as e:
        logger.error("APPRAISAL_ENDPOINT_FAILED", context={"error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to generate appraisal") from None


# --- ANALYTICS ENDPOINTS ---


@app.get("/api/analytics/qualification-metrics", dependencies=[Depends(get_current_user)])
async def get_qualification_metrics(days: int = Query(default=7, ge=1, le=90)) -> dict[str, Any]:
    """
    Get lead qualification flow metrics for the specified period.

    Returns completion rates, started/completed counts, and other analytics.
    """
    scorer = LeadScorer(container.db)
    metrics = scorer.calculate_completion_rate(days=days)

    return metrics


@app.get("/api/analytics/score-distribution", dependencies=[Depends(get_current_user)])
async def get_score_distribution(days: int = Query(default=30, ge=1, le=90)) -> dict[str, Any]:
    """
    Get the distribution of lead scores (HOT/WARM/COLD) for the specified period.
    """
    scorer = LeadScorer(container.db)
    distribution = scorer.get_score_distribution(days=days)

    return distribution


# --- PHASE 2: MARKET & OUTREACH ENDPOINTS ---


@app.get("/api/market/data", dependencies=[Depends(get_current_user)])
async def get_market_data(
    city: str | None = Query(None),
    zone: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
) -> dict[str, Any]:
    query = container.db.client.table("market_data").select("*")
    if city:
        query = query.eq("city", city)
    if zone:
        query = query.ilike("zone", f"%{zone}%")

    result = query.order("created_at", desc=True).limit(limit).execute()
    return {"status": "success", "data": result.data}


@app.get("/api/market/analysis", dependencies=[Depends(get_current_user)])
async def get_market_analysis(
    city: str = Query("Milano"),
    zone: str | None = Query(None),
) -> dict[str, Any]:
    """
    Returns AI-generated market analysis and combined statistics.
    """
    return container.market_intel.get_market_analysis(city, zone)


@app.get("/api/market/trends", dependencies=[Depends(get_current_user)])
async def get_market_trends(
    zone: str = Query(..., min_length=2),
    city: str = Query("Milano"),
) -> dict[str, Any]:
    """
    Returns predictive price trends for a specific zone.
    """
    return container.market_intel.predict_market_trend(zone, city)


@app.get("/api/outreach/targets", dependencies=[Depends(get_current_user)])
async def get_outreach_targets(
    city: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
) -> dict[str, Any]:
    query = container.db.client.table("outreach_targets").select("*")
    if city:
        query = query.eq("city", city)
    if status:
        query = query.eq("status", status)

    result = query.order("created_at", desc=True).limit(limit).execute()
    return {"status": "success", "data": result.data}


@app.post("/api/outreach/generate", dependencies=[Depends(get_current_user)])
async def generate_outreach_targets(req: OutreachGenerateRequest) -> dict[str, Any]:
    """
    Triggers the agency discovery logic and populates outreach_targets.
    """
    try:
        # Import late to avoid circular dependencies if any
        from scripts.agency_outreach import search_agencies  # noqa: PLC0415

        agencies = search_agencies(city=req.city)
        count = 0
        for agency in agencies:
            # Prepare data for upsert
            message = (
                f"Ciao {agency['name']}! Ho visto la vostra vetrina in {agency['address']}. "
                f"Ricevete lead notturni? La nostra AI li qualifica in 15 secondi su WhatsApp. "
                f"Vuoi vedere una demo?"
            )
            target = {
                "name": agency["name"],
                "phone": agency["phone"],
                "address": agency["address"],
                "city": agency["city"],
                "outreach_message": message,
                "status": "PENDING",
            }
            container.db.client.table("outreach_targets").upsert(
                target, on_conflict="phone"
            ).execute()
            count += 1

        return {"status": "success", "message": f"Generated {count} targets for {req.city}"}
    except Exception as e:
        logger.error("OUTREACH_GENERATION_FAILED", context={"error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to generate outreach targets") from None


@app.post("/api/outreach/send", dependencies=[Depends(get_current_user)])
async def send_outreach_message(req: OutreachSendRequest) -> dict[str, Any]:
    """
    Sends the outreach message to a specific target and updates status.
    """
    try:
        # 1. Fetch target from DB
        res = (
            container.db.client.table("outreach_targets")
            .select("*")
            .eq("id", req.target_id)
            .single()
            .execute()
        )
        target = res.data
        if not target:
            raise HTTPException(status_code=404, detail="Outreach target not found")

        # 2. Send message via container messaging port
        sid = container.msg.send_message(to=target["phone"], body=target["outreach_message"])

        # 3. Update status in DB
        container.db.client.table("outreach_targets").update(
            {"status": "CONTACTED", "last_contacted_at": datetime.now().isoformat()}
        ).eq("id", req.target_id).execute()

        logger.info("OUTREACH_MESSAGE_SENT", context={"target_id": req.target_id, "sid": sid})

        return {"status": "success", "message": "Outreach message sent.", "sid": sid}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("OUTREACH_SEND_FAILED", context={"target_id": req.target_id, "error": str(e)})
        raise HTTPException(status_code=500, detail=f"Failed to send outreach: {str(e)}") from None


@app.post("/api/reports/sales", dependencies=[Depends(get_current_user)])
async def generate_sales_report_endpoint(req: SalesReportRequest) -> dict[str, Any]:
    """
    Generates a PDF sales report for a specific property.
    """
    try:
        # 1. Fetch property and lead activity
        # This is a bit complex, we'll mock some parts for now or use DB queries
        res = (
            container.db.client.table("properties")
            .select("*")
            .eq("id", req.property_id)
            .single()
            .execute()
        )
        prop = res.data
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")

        # 2. Fetch leads interested in this property
        # Query leads where metadata->interested_property_ids contains req.property_id
        leads_res = (
            container.db.client.table("leads")
            .select("id, status, score, journey_state, metadata")
            .execute()
        )

        # Filter in Python if complex JSONB query is tricky via client,
        # but let's try to be efficient if possible.
        # Actually, let's filter in Python for now to be safe with the metadata structure
        # Constants for lead analysis
        hot_lead_threshold = 50
        min_leads_for_optimal_price = 10
        min_hot_leads_for_quick_close = 3

        all_leads = leads_res.data or []
        interested_leads = []
        for lead_data in all_leads:
            meta = lead_data.get("metadata") or {}
            if req.property_id in meta.get("interested_property_ids", []):
                interested_leads.append(lead_data)

        total_leads = len(interested_leads)
        hot_leads = len(
            [
                lead_data
                for lead_data in interested_leads
                if (lead_data.get("score") or 0) >= hot_lead_threshold
            ]
        )
        scheduled_viewings = len(
            [
                lead_data
                for lead_data in interested_leads
                if lead_data.get("journey_state") == "SCHEDULED"
            ]
        )

        # 3. Dynamic Analysis/Advice based on data
        zone_name = prop.get("zone", "N/A")
        market_analysis = (
            f"La zona di {zone_name} mostra un interesse costante. "
            f"La proprietà ha attirato {total_leads} potenziali acquirenti."
        )
        if total_leads > min_leads_for_optimal_price:
            market_analysis += " Il posizionamento prezzo è ottimale."
        else:
            market_analysis += (
                " Valutare un leggero ribasso o nuove foto per " "aumentare il click-through rate."
            )

        ai_advice = "Monitorare i lead 'Hot' e sollecitare il feedback post-visita."
        if hot_leads > MIN_HOT_LEADS_FOR_QUICK_CLOSE:
            ai_advice = (
                "Alta probabilità di chiusura breve. "
                "Concentrarsi sui 3 lead più caldi per negoziazione."
            )

        report_data = {
            "property_id": req.property_id,
            "property_title": prop["title"],
            "total_leads": total_leads,
            "hot_leads": hot_leads,
            "scheduled_viewings": scheduled_viewings,
            "market_value": prop["price"],
            "market_analysis": market_analysis,
            "ai_advice": ai_advice,
        }

        # 4. Generate PDF
        pdf_path = container.doc_gen.generate_pdf("sales_report", report_data)

        return {
            "status": "success",
            "pdf_path": pdf_path,
            "filename": os.path.basename(pdf_path),
            "message": "Report vendite generato con successo",
        }
    except Exception as e:
        logger.error(
            "SALES_REPORT_FAILED", context={"property_id": req.property_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to generate sales report") from None


class RouteLeadRequest(BaseModel):
    """Request to manually route a lead to a specific agent."""

    lead_id: str
    agent_id: str | None = None


@app.post("/api/admin/route-lead", dependencies=[Depends(get_current_user)])
async def route_lead_endpoint(req: RouteLeadRequest) -> dict[str, Any]:
    """
    Manually route a lead to an agent or trigger auto-routing based on score.
    """
    scorer = LeadScorer(container.db)

    # Get lead's qualification data
    lead_response = (
        container.db.client.table("leads").select("*").eq("id", req.lead_id).single().execute()
    )
    lead_data: dict[str, Any] = lead_response.data

    # Calculate score if not  already done
    if not lead_data.get("lead_score_normalized"):
        qual_data = QualificationData(**lead_data)
        score = ScoringService.calculate_score(qual_data)
    else:
        # Use existing score
        score = LeadScore(
            raw_score=lead_data.get("lead_score_raw", 0),
            normalized_score=lead_data["lead_score_normalized"],
            category=LeadCategory(lead_data.get("lead_category", "COLD")),
            details=QualificationData(**lead_data),
            action_item="",
        )

    # Route the lead
    agent_uuid = UUID(req.agent_id) if req.agent_id else None
    routing_result = scorer.route_lead(lead_id=UUID(req.lead_id), score=score, agent_id=agent_uuid)

    return routing_result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
