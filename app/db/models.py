from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import sqlalchemy as sa

class Base(DeclarativeBase):
    pass


class Lead(Base):
    __tablename__ = "leads"

    __table_args__ = (
        CheckConstraint(
            "status IN ('New', 'Contacted', 'Booked', 'Closed')",
            name="ck_leads_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(
        String(254),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
    )

    preferred_contact: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'email'"),
    )

    whatsapp_consent: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    whatsapp_consent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    course: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'New'"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    ai_analysis: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    ai_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    ai_prompt_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    ai_analysed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

class NotificationJob(Base):
    __tablename__ = "notification_jobs"

    __table_args__ = (
        sa.UniqueConstraint(
            "lead_id",
            "event_type",
            name="uq_notification_jobs_lead_event",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'processing', 'succeeded', 'failed')",
            name="ck_notification_jobs_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    lead_id: Mapped[int] = mapped_column(
        sa.ForeignKey("leads.id"),
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'new_lead'"),
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'pending'"),
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    locked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_error: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )