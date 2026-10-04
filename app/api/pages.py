from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


APP_DIR = Path(__file__).resolve().parents[1]

router = APIRouter()
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))


@router.get("/enquiry", response_class=HTMLResponse)
def enquiry_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="enquiry.html",
        context={},
    )
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={},
    )