from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.sql import func
from pydantic import BaseModel
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Orders Service")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Page d'accueil avec navigation
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Liste des commandes
@app.get("/orders", response_class=HTMLResponse)
def list_orders(request: Request, db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return templates.TemplateResponse("orders.html", {"request": request, "orders": orders})

# Formulaire ajout commande - GET
@app.get("/orders/add", response_class=HTMLResponse)
def add_order_form(request: Request):
    return templates.TemplateResponse("order_form.html", {"request": request, "action": "Add", "order": None})

# Ajout commande - POST
@app.post("/orders/add", response_class=HTMLResponse)
def add_order(
    request: Request,
    user_id: int = Form(...),
    product_id: int = Form(...),
    db: Session = Depends(get_db)
):
    order = Order(user_id=user_id, product_id=product_id)
    db.add(order)
    db.commit()
    return RedirectResponse(url="/orders", status_code=status.HTTP_303_SEE_OTHER)

# Suppression commande
@app.get("/orders/delete/{order_id}", response_class=HTMLResponse)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return RedirectResponse(url="/orders", status_code=status.HTTP_303_SEE_OTHER)

