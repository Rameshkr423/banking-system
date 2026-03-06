from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.user_service import create_user, search_users
from app.schemas.user import UserCreate, UserWithAccountResponse

router = APIRouter()


# ---------------------------------------------------
# Search Users
# ---------------------------------------------------
@router.get("/search")
def search_user(query: str, db: Session = Depends(get_db)):
    return search_users(db, query)

@router.post("/", response_model=UserWithAccountResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    result = create_user(db, user)

    return {
        "id": result["user"].id,
        "full_name": result["user"].full_name,
        "email": result["user"].email,
        "phone": result["user"].phone,
        "account": result["account"]
    }