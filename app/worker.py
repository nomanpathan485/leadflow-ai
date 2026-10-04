import logging
import signal
from datetime import datetime, timedelta, timezone
from threading import Event

import httpx
from sqlalchemy import select

from app.config import get_settings
from app.db.connection import SessionLocal
from app.db.models import NotificationJob


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("leadflow.worker")

stop_event = Event()
MAX_ATTEMPTS = 5


def request_shutdown(signum, frame):
    stop_event.set()


def process_one_job(client: httpx.Client) -> bool:
    settings = get_settings()

    # Keep the row lock until the request outcome is saved.
    with SessionLocal.begin() as session:
        job = session.scalar(
            select(NotificationJob)
            .where(
                NotificationJob.status == "pending",
                NotificationJob.available_at <= datetime.now(timezone.utc),
            )
            .order_by(NotificationJob.available_at, NotificationJob.id)
            .with_for_update(skip_locked=True)
            .limit(1)
        )

        if job is None:
            return False

        job.status = "processing"
        job.locked_at = datetime.now(timezone.utc)
        job.attempts += 1

        logger.info(
            "Sending job=%s lead=%s attempt=%s",
            job.id,
            job.lead_id,
            job.attempts,
        )

        try:
            response = client.post(
                settings.n8n_webhook_url,
                headers={
                    "X-LeadFlow-Token": (
                        settings.n8n_webhook_secret.get_secret_value()
                    ),
                },
                json={
                    "job_id": job.id,
                    "lead_id": job.lead_id,
                    "event_type": job.event_type,
                },
            )
            response.raise_for_status()

        except httpx.HTTPError as exc:
            # Store only an error category, not secrets or response bodies.
            if isinstance(exc, httpx.HTTPStatusError):
                error = f"HTTP {exc.response.status_code}"
            else:
                error = type(exc).__name__

            job.last_error = error
            job.locked_at = None

            if job.attempts >= MAX_ATTEMPTS:
                job.status = "failed"
                logger.error(
                    "Job=%s exhausted retries: %s",
                    job.id,
                    error,
                )
            else:
                delay_seconds = min(
                    30 * (2 ** (job.attempts - 1)),
                    300,
                )
                job.status = "pending"
                job.available_at = (
                    datetime.now(timezone.utc)
                    + timedelta(seconds=delay_seconds)
                )
                logger.warning(
                    "Job=%s retry in %ss: %s",
                    job.id,
                    delay_seconds,
                    error,
                )
        else:
            job.status = "succeeded"
            job.completed_at = datetime.now(timezone.utc)
            job.locked_at = None
            job.last_error = None

            logger.info("Job=%s webhook succeeded", job.id)

    return True


def main():
    signal.signal(signal.SIGTERM, request_shutdown)
    signal.signal(signal.SIGINT, request_shutdown)

    logger.info("Notification worker started")

    with httpx.Client(
        timeout=httpx.Timeout(30.0, connect=5.0),
        follow_redirects=False,
    ) as client:
        while not stop_event.is_set():
            try:
                processed = process_one_job(client)
            except Exception as exc:
                # An unexpected failure rolls back the transaction.
                logger.error(
                    "Worker cycle failed: %s",
                    type(exc).__name__,
                )
                stop_event.wait(5)
            else:
                if not processed:
                    stop_event.wait(2)

    logger.info("Notification worker stopped")


if __name__ == "__main__":
    main()