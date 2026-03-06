from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy import or_

from app.models.user import User
from app.models.account import Account, AccountType
from app.models.bank import Bank
from app.models.branch import Branch
from app.models.city import City
from app.utils.account_number import generate_account_number


def search_users(db: Session, query: str):

    users = (
        db.query(User, Account, Bank, Branch, City)
        .join(Account, Account.user_id == User.id)
        .join(Bank, Bank.id == Account.bank_id)
        .join(Branch, Branch.id == Account.branch_id)
        .join(City, City.id == User.city_id)
        .filter(
            or_(
                User.full_name.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%"),
                User.phone.ilike(f"%{query}%"),
                User.address_line.ilike(f"%{query}%"),
                User.area.ilike(f"%{query}%"),
                User.zipcode.ilike(f"%{query}%"),
                Account.account_number.ilike(f"%{query}%"),
                Bank.bank_name.ilike(f"%{query}%"),
                Branch.branch_name.ilike(f"%{query}%"),
                City.city_name.ilike(f"%{query}%")
            )
        )
        .limit(50)
        .all()
    )

    result = []

    for user, account, bank, branch, city in users:

        result.append({
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "address_line": user.address_line,
            "area": user.area,
            "zipcode": user.zipcode,

            "city": city.city_name,

            "account_number": account.account_number,
            "account_type": account.account_type,

            "bank_name": bank.bank_name,
            "branch_name": branch.branch_name
        })

    return result


    for user, account in users:
        result.append({
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "address_line": user.address_line,
            "city": user.city,
            "area": user.area,
            "zipcode": user.zipcode,
            "state": user.state,
            "country": user.country,
            "account_number": account.account_number,
            "account_type": account.account_type
        })

    return result


def create_user(db: Session, user_data):
    try:

        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            phone=user_data.phone,
            address_line=user_data.address_line,
            area=user_data.area,
            zipcode=user_data.zipcode,
            city_id=user_data.city_id
        )

        db.add(user)
        db.flush()

        account = Account(
            user_id=user.id,
            account_number=generate_account_number(),
            account_type=AccountType.savings,
            bank_id=user_data.bank_id,
            branch_id=user_data.branch_id
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
