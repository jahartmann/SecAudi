from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
import requests

from . import models, database

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

models.Base.metadata.create_all(bind=database.engine)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(database.get_db)):
    servers = db.query(models.Server).all()
    return templates.TemplateResponse("index.html", {"request": request, "servers": servers})


@app.post("/servers")
def create_server(
    name: str = Form(...),
    host: str = Form(...),
    ssh_key: str = Form("") ,
    db: Session = Depends(database.get_db),
):
    server = models.Server(name=name, host=host, ssh_key=ssh_key)
    db.add(server)
    db.commit()
    return RedirectResponse("/", status_code=303)


@app.post("/servers/{server_id}/audit")
def run_audit(server_id: int, db: Session = Depends(database.get_db)):
    server = db.query(models.Server).get(server_id)
    report = f"# Audit report for {server.name}\nPlaceholder report"
    rating = "Mittel"
    audit = models.Audit(
        server_id=server.id,
        rating=rating,
        report_markdown=report,
        scorecard_json="{}",
    )
    db.add(audit)
    db.commit()
    return RedirectResponse(f"/audits/{audit.id}", status_code=303)


@app.get("/settings", response_class=HTMLResponse)
def settings(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})


@app.post("/settings")
def save_settings(request: Request, host: str = Form(...), port: int = Form(...)):
    request.app.state.ollama_host = host
    request.app.state.ollama_port = port
    return RedirectResponse("/settings", status_code=303)


@app.get("/settings/models")
def list_models(request: Request):
    host = getattr(request.app.state, "ollama_host", "localhost")
    port = getattr(request.app.state, "ollama_port", 11434)
    try:
        resp = requests.get(f"http://{host}:{port}/api/tags", timeout=5)
        models_list = [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        models_list = []
    return {"models": models_list}


@app.get("/audits", response_class=HTMLResponse)
def audits(request: Request, db: Session = Depends(database.get_db)):
    audits = (
        db.query(models.Audit)
        .options(joinedload(models.Audit.server))
        .order_by(models.Audit.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        "audits.html", {"request": request, "audits": audits}
    )


@app.get("/audits/{audit_id}", response_class=HTMLResponse)
def audit_detail(audit_id: int, request: Request, db: Session = Depends(database.get_db)):
    audit = (
        db.query(models.Audit)
        .options(joinedload(models.Audit.server))
        .filter(models.Audit.id == audit_id)
        .first()
    )
    return templates.TemplateResponse(
        "audit_detail.html", {"request": request, "audit": audit}
    )
