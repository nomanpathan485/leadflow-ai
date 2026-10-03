from app.db.repository import save_lead, get_leads, update_lead_status
from fastapi import FastAPI, HTTPException
from app.schemas import LeadInput, LeadStatusUpdate

app = FastAPI(title="LeadFlow AI")

@app.get("/")
def home():
    return {"message": "LeadFlow API is running"}


@app.post("/leads/preview")
def preview_lead(lead: LeadInput):
    return {
        "message": "Enquiry validated successfully",
        "lead": lead.model_dump(),
    }


@app.post("/leads", status_code=201)
def create_lead(lead: LeadInput):
    lead_id = save_lead(
        name=lead.name,
        email=str(lead.email),
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