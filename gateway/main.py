from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

SERVICES = {
  "users": os.getenv("USERS_URL", "http://localhost:8001"),
  "products": os.getenv("PRODUCTS_URL", "http://localhost:8002"),
  "orders": os.getenv("ORDERS_URL", "http://localhost:8003"),
}

app = FastAPI(title="API Gateway")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "services": SERVICES.keys()})


@app.get("/{service}/")
async def service_list(request: Request, service: str):
    base = SERVICES.get(service)
    if not base:
        raise HTTPException(status_code=404, detail="unknown service")
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{base}/")
        r.raise_for_status()
        items = r.json()
    return templates.TemplateResponse(
        "service_list.html",
        {"request": request, "service": service, "items": items}
    )


@app.get("/{service}/create")
async def create_form(request: Request, service: str):
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="unknown service")
    return templates.TemplateResponse("create_form.html", {"request": request, "service": service})


@app.post("/{service}/create")
async def create_item(request: Request, service: str):
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="unknown service")
    form = await request.form()
    payload = dict(form)
    base = SERVICES[service]
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{base}/", json=payload)
        r.raise_for_status()
    return RedirectResponse(url=f"/{service}/", status_code=303)


@app.get("/{service}/{item_id}")
async def item_detail(request: Request, service: str, item_id: int):
    base = SERVICES.get(service)
    if not base:
        raise HTTPException(status_code=404, detail="unknown service")
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{base}/{item_id}")
        r.raise_for_status()
        item = r.json()
    return templates.TemplateResponse(
        "item_detail.html",
        {"request": request, "service": service, "item": item}
    )
