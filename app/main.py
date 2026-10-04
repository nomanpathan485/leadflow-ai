from app.db.repository import save_lead, get_leads, update_lead_status, get_lead
from fastapi import FastAPI, HTTPException
from app.schemas import LeadInput, LeadStatusUpdate
from app.api.health import router as health_router
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from app.api.analysis import router as analysis_router
from app.api.pages import router as pages_router

app = FastAPI(title="LeadFlow AI")
app.include_router(analysis_router)
APP_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=str(APP_DIR / "static")),
    name="static",
)

app.include_router(pages_router)
app.include_router(health_router)
@app.get("/")
def home():
    return {"message": "LeadFlow API is running"}


@app.post("/leads/preview")
def preview_lead(lead: LeadInput):
    return {
        "message": "Enquiry validated successfully",
        "lead": lead.model_dump(),
    }
@app.get("/leads/{lead_id}")
def retrieve_lead(lead_id: int):
    lead = get_lead(lead_id)

    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    return lead

@app.post("/leads", status_code=201)
def create_lead(lead: LeadInput):
    lead_id = save_lead(
        name=lead.name,
        email=str(lead.email) if lead.email is not None else None,
        phone=lead.phone,
        preferred_contact=lead.preferred_contact,
        whatsapp_consent=lead.whatsapp_consent,
        course=lead.course,
        message=lead.message,
    )

    return {
        "message": "Enquiry saved successfully",
        "lead_id": lead_id,
        "status": "New",
    }

@app.get("/leads")
def list_leads():
    return get_leads()

@app.patch("/leads/{lead_id}/status")
def change_lead_status(lead_id: int, update: LeadStatusUpdate):
    found = update_lead_status(lead_id, update.status)

    if not found:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    return {
        "message": "Status updated successfully",
        "lead_id": lead_id,
        "status": update.status,
    }

