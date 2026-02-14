from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.user import User
from app.models.account import Account, AccountType
from app.utils.account_number import generate_account_number

  

def create_user(db: Session, user_data):
    try:
        user = User(**user_data.dict())
        db.add(user)
        db.flush()

        account = Account(
            user_id=user.id,
            account_number=generate_account_number(),
            account_type=AccountType.savings
        )

        db.add(account)
        db.commit()

        db.refresh(user)
        db.refresh(account)

        return {
            "user": user,
            "account": account
        }

    except IntegrityError as e:
        db.rollback()

        if "users.phone" in str(e):
            raise HTTPException(status_code=409, detail="Phone number already registered")

        if "users.email" in str(e):
            raise HTTPException(status_code=409, detail="Email already registered")

        raise HTTPException(status_code=400, detail="Database error")
