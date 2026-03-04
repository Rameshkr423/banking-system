import random
import uuid
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.user_service import create_user
from app.services.transaction_service import deposit, transfer
from app.schemas.user import UserCreate


def run_simulation(
    db: Session,
    accounts: int,
    transfers_per_account: int,
    initial_deposit: int
):

    created_accounts = []

    try:

        # -----------------------------------
        # Step 1: Create Users + Accounts
        # -----------------------------------
        for _ in range(accounts):

            user_data = UserCreate(
                full_name=f"Test User {uuid.uuid4().hex[:6]}",
                email=f"user_{uuid.uuid4().hex[:6]}@test.com",
                phone=str(random.randint(9000000000, 9999999999))
            )

            result = create_user(db, user_data)
            account = result["account"]

            # Initial deposit
            deposit(db, account.id, Decimal(initial_deposit))

            created_accounts.append(account.id)

        # -----------------------------------
        # Step 2: Random Transfers
        # -----------------------------------
        total_transfers = accounts * transfers_per_account
        executed = 0

        while executed < total_transfers:

            from_acc, to_acc = random.sample(created_accounts, 2)

            amount = Decimal(random.randint(1, 10))

            try:

                transfer(
                    db,
                    from_acc,
                    to_acc,
                    amount,
                    idempotency_key=str(uuid.uuid4())
                )

                executed += 1

            except Exception:
                # Ignore failed transfers (ex: insufficient balance)
                db.rollback()

        # -----------------------------------
        # Final Commit
        # -----------------------------------
        db.commit()

        return {
            "accounts_created": accounts,
            "total_transfers": executed
        }

    except Exception as e:
        db.rollback()
        raise e