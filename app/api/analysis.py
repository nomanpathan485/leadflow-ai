import logging

from fastapi import APIRouter, HTTPException
from groq import APIError
from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError

from app.ai.extractor import PROMPT_VERSION, analyse_enquiry
from app.config import get_settings
from app.db.repository import (
    get_lead_for_analysis,
    save_lead_analysis,
)


router = APIRouter(prefix="/leads", tags=["AI analysis"])
logger = logging.getLogger(__name__)


@router.post("/{lead_id}/analyse")
def analyse_lead(lead_id: int):
    lead = get_lead_for_analysis(lead_id)

    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    if lead["ai_analysis"] is not None:
        return {
            "lead_id": lead_id,
            "analysis": lead["ai_analysis"],
            "cached": True,
        }

    settings = get_settings()

    if (
        settings.groq_api_key is None
        or not settings.groq_api_key.get_secret_value().strip()
    ):
        raise HTTPException(
            status_code=503,
            detail="AI analysis is not configured.",
        )

    try:
        result = analyse_enquiry(
            course=lead["course"],
            message=lead["message"],
        )
    except (APIError, OutputParserException, ValidationError) as exc:
        # Record the error category without logging customer data or API keys.
        logger.warning(
            "AI analysis failed for lead %s: %s",
            lead_id,
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=502,
            detail="AI analysis failed. Your enquiry is saved; try again later.",
        ) from None

    analysis = result.model_dump(mode="json")

    saved = save_lead_analysis(
        lead_id=lead_id,
        analysis=analysis,
        model=settings.groq_model,
        prompt_version=PROMPT_VERSION,
    )

    if not saved:
        raise HTTPException(status_code=404, detail="Lead not found")

    return {
        "lead_id": lead_id,
        "analysis": analysis,
        "cached": False,
    }