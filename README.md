# LeadFlow AI

An enquiry-management MVP for training institutes, combining structured AI analysis with automated WhatsApp alerts.

Built by **Noman Ayyub Pathan**.

## The problem

Student enquiries can arrive while staff are busy. Without a shared tracker, follow-ups become difficult to manage.

LeadFlow captures enquiries, stores contact preferences, extracts useful information with an LLM, and alerts the institute owner through WhatsApp.

## Features

- Student enquiry form with submission confirmation.
- Optional email and phone details with contact-preference validation.
- Explicit consent capture for WhatsApp contact.
- Dashboard with enquiry statuses and manual follow-up links.
- Structured AI extraction of course interest, timing, and requested information.
- Stored AI results with model, prompt version, and analysis timestamp.
- Persistent notification jobs created in the same transaction as each lead.
- Separate notification worker with retries and recorded failures.
- n8n workflow for fetching lead details and sending WhatsApp alerts.
- Database migrations and health endpoints.

## Technology

| Component | Technology |
|-----------|------------|
| Backend | Python, FastAPI, Pydantic |
| Database | PostgreSQL, SQLAlchemy |
| Migrations | Alembic |
| AI extraction | LangChain, Groq |
| Automation | n8n |
| Notifications | WhatsApp Business Cloud |
| Interface | HTML, CSS, JavaScript |
| Local deployment | Docker Compose |

## How it works

1. A student submits an enquiry.
2. FastAPI validates the input.
3. PostgreSQL saves the lead and its notification job together.
4. A separate worker selects an available job using a database row lock.
5. The worker calls an authenticated n8n webhook.
6. n8n retrieves the lead and sends an owner WhatsApp alert.
7. The worker records success or schedules a retry.

AI analysis is currently triggered manually from the dashboard. It is separate from the notification pipeline.

## Local setup

### Requirements

- Docker Desktop with Docker Compose.
- A Groq API key for AI analysis.
- Meta WhatsApp Business Cloud test or production credentials.

### Configure environment variables

Copy the example configuration:

```powershell
Copy-Item .env.example .env
```

Set the database password, Groq configuration, and n8n webhook secret.

The webhook URL used by Docker services is:

```dotenv
N8N_WEBHOOK_URL=http://n8n:5678/webhook/leadflow-new-enquiry
```

Never commit `.env` or actual credentials.

### Start infrastructure and apply migrations

```powershell
docker compose up -d postgres n8n
docker compose build api worker
docker compose run --rm --no-deps api python -m alembic upgrade head
```

### Configure n8n

1. Open http://localhost:5678 and complete account setup.
2. Import `workflows/new-lead-whatsapp-alert.json`.
3. Create a Header Auth credential:
   - Header name: `X-LeadFlow-Token`
   - Value: the same secret as `N8N_WEBHOOK_SECRET`.
4. Select that credential in the Webhook node.
5. Configure the WhatsApp Business Cloud credential.
6. Replace the sender ID and owner recipient placeholders.
7. Keep the webhook response set to `When Last Node Finishes`.
8. Keep downstream nodes configured to stop the workflow on error.
9. Publish the workflow.

WhatsApp test recipients must be configured through Meta. Free-form messages are subject to WhatsApp's customer-service window; approved templates are needed outside that window.

### Start the application

```powershell
docker compose up -d api worker
```

| Page | Local URL |
|------|-----------|
| Enquiry form | http://localhost:8000/enquiry |
| Dashboard | http://localhost:8000/dashboard |
| API documentation | http://localhost:8000/docs |
| Readiness check | http://localhost:8000/health/ready |
| n8n | http://localhost:5678 |

### Inspect notification jobs

```powershell
docker compose logs --tail=50 worker
```

```powershell
docker compose exec postgres psql -U leadflow -d leadflow -c "SELECT id, lead_id, status, attempts, last_error FROM notification_jobs ORDER BY id DESC LIMIT 10;"
```

## Current limitations

This is a local MVP with production-oriented foundations.

- Staff authentication and authorization are not implemented.
- A successful job means the webhook returned success, not confirmed WhatsApp delivery.
- Retries can produce duplicate messages after ambiguous failures.
- The initial worker holds a database transaction during the HTTP request.
- Automated tests, monitoring, backups, and deployment hardening remain planned.
- AI extraction can make mistakes and requires human review.
- Included courses are demonstration options, not a verified institute catalogue.

Use fake enquiries for public demonstrations.

## Next improvements

- Authentication and protected dashboard access.
- Retry recovery and failure-path tests.
- Duplicate-send handling and delivery-status tracking.
- AI extraction evaluation.
- Monitoring, backups, and production deployment.