from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv
from prometheus_fastapi_instrumentator import Instrumentator


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Users Service")

templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup():
    Instrumentator().instrument(app).expose(app)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/users", response_class=HTMLResponse)
def list_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("users_list.html", {"request": request, "users": users})

@app.get("/users/add", response_class=HTMLResponse)
def add_user_form(request: Request):
    return templates.TemplateResponse("users_add.html", {"request": request})

@app.post("/users/add", response_class=HTMLResponse)
def add_user(request: Request, name: str = Form(...), email: EmailStr = Form(...), db: Session = Depends(get_db)):
    user = User(name=name, email=email)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse("users_add.html", {"request": request, "error": "Email déjà existant"})
    return RedirectResponse(url="/users", status_code=303)

@app.get("/users/edit/{user_id}", response_class=HTMLResponse)
def edit_user_form(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        return RedirectResponse(url="/users")
    return templates.TemplateResponse("users_edit.html", {"request": request, "user": user})

@app.post("/users/edit/{user_id}", response_class=HTMLResponse)
def edit_user(request: Request, user_id: int, name: str = Form(...), email: EmailStr = Form(...), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        return RedirectResponse(url="/users")
    user.name = name
    user.email = email
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse("users_edit.html", {"request": request, "user": user, "error": "Email déjà existant"})
    return RedirectResponse(url="/users", status_code=303)

@app.get("/users/delete/{user_id}", response_class=HTMLResponse)
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user:
        db.delete(user)
        db.commit()
    return RedirectResponse(url="/users", status_code=303)
