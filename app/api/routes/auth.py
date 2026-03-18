from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse, DashboardResponse
from app.services.auth_service import login, get_dashboard
from app.core.security import get_current_user_id

router = APIRouter()

# -------------------------------------------------------
# POST /auth/login
# -------------------------------------------------------
@router.post("/login", response_model=TokenResponse, summary="Login with Phone & Password")
def auth_login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login using phone number and password.
    Returns a JWT Bearer token to use in protected routes.
    """
    return login(db, request.phone, request.password)


# -------------------------------------------------------
# GET /auth/dashboard
# -------------------------------------------------------
@router.get("/dashboard", response_model=DashboardResponse, summary="Home Dashboard")
def dashboard(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Protected route - requires Bearer token from /auth/login.
    Returns account balances + last 10 transactions.
    """
    return get_dashboard(db, user_id)