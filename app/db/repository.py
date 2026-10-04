from sqlalchemy import select, update
from datetime import datetime, timezone
from app.db.connection import SessionLocal
from app.db.models import Lead, NotificationJob


def save_lead(
    name: str,
    email: str | None,
    course: str,
    message: str,
    phone: str | None = None,
    preferred_contact: str = "email",
    whatsapp_consent: bool = False,
) -> int:
    with SessionLocal.begin() as session:
        lead = Lead(
            name=name,
            email=email,
            phone=phone,
            preferred_contact=preferred_contact,
            whatsapp_consent=whatsapp_consent,
            whatsapp_consent_at=(
                datetime.now(timezone.utc)
                if whatsapp_consent
                else None
            ),
            course=course,
            message=message,
        )

        session.add(lead)
        session.flush()
        lead_id = lead.id
        session.add(
            NotificationJob(
                lead_id=lead_id,
                event_type="new_lead",
            )
        )

    return lead_id


def get_leads() -> list[dict]:
    with SessionLocal() as session:
        leads = session.scalars(
            select(Lead).order_by(Lead.id.desc())
        ).all()

        return [
            {
                "id": lead.id,
                "name": lead.name,
                "email": lead.email,
                "phone": lead.phone,
                "preferred_contact": lead.preferred_contact,
                "whatsapp_consent": lead.whatsapp_consent,
                "whatsapp_consent_at": lead.whatsapp_consent_at,
                "course": lead.course,
                "message": lead.message,
                "status": lead.status,
                "created_at": lead.created_at,
                "ai_analysis": lead.ai_analysis,
                "ai_model": lead.ai_model,
                "ai_prompt_version": lead.ai_prompt_version,
                "ai_analysed_at": lead.ai_analysed_at,
            }
            for lead in leads
        ]


def update_lead_status(lead_id: int, status: str) -> bool:
    with SessionLocal.begin() as session:
        result = session.execute(
            update(Lead)
            .where(Lead.id == lead_id)
            .values(status=status)
        )

        found = result.rowcount > 0

    return found

def get_lead_for_analysis(lead_id: int) -> dict | None:
    with SessionLocal() as session:
        lead = session.get(Lead, lead_id)

        if lead is None:
            return None

        return {
            "id": lead.id,
            "course": lead.course,
            "message": lead.message,
            "ai_analysis": lead.ai_analysis,
        }


def save_lead_analysis(
    lead_id: int,
    analysis: dict,
    model: str,
    prompt_version: str,
) -> bool:
    with SessionLocal.begin() as session:
        result = session.execute(
            update(Lead)
            .where(Lead.id == lead_id)
            .values(
                ai_analysis=analysis,
                ai_model=model,
                ai_prompt_version=prompt_version,
                ai_analysed_at=datetime.now(timezone.utc),
            )
        )

        found = result.rowcount > 0

    return found

def get_lead(lead_id: int) -> dict | None:
    with SessionLocal() as session:
        lead = session.get(Lead, lead_id)

        if lead is None:
            return None

        return {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "preferred_contact": lead.preferred_contact,
            "course": lead.course,
            "message": lead.message,
            "status": lead.status,
            "created_at": lead.created_at,
        }