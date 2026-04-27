from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.database import get_db
from app.services import auth_service
from app.i18n.locales import get_country_config, get_currency_for_country, get_language_for_country, COUNTRY_CONFIG

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""
    country: str = "FR"
    language: Optional[str] = None  # auto-detected from country if not set


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth_service.decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = auth_service.get_user_by_email(db, payload.get("sub", ""))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if auth_service.get_user_by_email(db, req.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    country = req.country.upper()
    config = get_country_config(country)
    language = req.language or config["language"]
    currency = config["currency"]
    timezone = config["timezone"]

    user = auth_service.create_user(db, req.email, req.password, req.full_name)
    user.country = country
    user.language = language
    user.currency = currency
    user.timezone = timezone
    db.commit()

    token = auth_service.create_access_token({"sub": user.email})
    return {"access_token": token}


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth_service.create_access_token({"sub": user.email})
    return {"access_token": token}


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "language": current_user.language,
        "country": current_user.country,
        "currency": current_user.currency,
        "timezone": current_user.timezone,
    }


@router.get("/countries")
def list_countries():
    return [
        {"code": code, "name": cfg["name"], "language": cfg["language"],
         "currency": cfg["currency"], "timezone": cfg["timezone"]}
        for code, cfg in COUNTRY_CONFIG.items()
    ]


@router.patch("/me/locale")
def update_locale(
    country: Optional[str] = None,
    language: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if country:
        config = get_country_config(country.upper())
        user.country = country.upper()
        user.currency = config["currency"]
        user.timezone = config["timezone"]
        if not language:
            user.language = config["language"]
    if language:
        user.language = language
    db.commit()
    return {"status": "updated", "language": user.language, "country": user.country, "currency": user.currency}
