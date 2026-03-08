from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.user_service import create_user, search_users
from app.schemas.user import UserCreate, UserWithAccountResponse
from app.core.security import get_current_user_id  # ⭐ Add this import


router = APIRouter()


# ---------------------------------------------------
# Search Users  🔒 Protected
# ---------------------------------------------------
@router.get("/search")
def search_user(
    query: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),  # ⭐ Auth
):
    return search_users(db, query)


# ---------------------------------------------------
# Register User
# ---------------------------------------------------
@router.post("/", response_model=UserWithAccountResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)   # ✅ return directly