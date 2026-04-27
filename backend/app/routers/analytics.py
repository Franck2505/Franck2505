from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers.auth import get_current_user
from app.services.analytics_service import get_dashboard_stats, get_platform_revenue_stats

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
def dashboard_stats(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_dashboard_stats(db, str(user.id))


@router.get("/revenue")
def revenue_stats(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role.value != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403)
    return get_platform_revenue_stats(db)
