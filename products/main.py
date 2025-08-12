from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False, default=0.0)

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Page d'accueil avec liens vers actions
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Liste des produits
@app.get("/products", response_class=HTMLResponse)
def list_products(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return templates.TemplateResponse("products.html", {"request": request, "products": products})

# Formulaire ajout produit - GET
@app.get("/products/add", response_class=HTMLResponse)
def add_product_form(request: Request):
    return templates.TemplateResponse("product_form.html", {"request": request, "action": "Add", "product": None})

# Ajout produit - POST
@app.post("/products/add", response_class=HTMLResponse)
def add_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    db: Session = Depends(get_db)
):
    product = Product(name=name, description=description, price=price)
    db.add(product)
    db.commit()
    return RedirectResponse(url="/products", status_code=status.HTTP_303_SEE_OTHER)

# Formulaire modification produit - GET
@app.get("/products/edit/{product_id}", response_class=HTMLResponse)
def edit_product_form(product_id: int, request: Request, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return templates.TemplateResponse("product_form.html", {"request": request, "action": "Edit", "product": product})

# Modification produit - POST
@app.post("/products/edit/{product_id}", response_class=HTMLResponse)
def edit_product(
    product_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    db: Session = Depends(get_db)
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.name = name
    product.description = description
    product.price = price
    db.commit()
    return RedirectResponse(url="/products", status_code=status.HTTP_303_SEE_OTHER)

# Suppression produit
@app.get("/products/delete/{product_id}", response_class=HTMLResponse)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return RedirectResponse(url="/products", status_code=status.HTTP_303_SEE_OTHER)
