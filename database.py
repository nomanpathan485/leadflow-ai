from sqlalchemy import select, update

from db_connection import SessionLocal
from models import Lead


def save_lead(name: str, email: str, course: str, message: str) -> int:
    with SessionLocal.begin() as session:
        lead = Lead(
            name=name,
            email=email,
            course=course,
            message=message,
        )

        session.add(lead)
        session.flush()
        lead_id = lead.id

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
                "course": lead.course,
                "message": lead.message,
                "status": lead.status,
                "created_at": lead.created_at,
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