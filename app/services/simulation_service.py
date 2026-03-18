import random
import uuid
import logging
from decimal import Decimal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException

from app.models.user import User
from app.models.account import Account
from app.models.bank import Bank
from app.models.branch import Branch
from app.models.city import City
from app.services.transaction_service import deposit, transfer

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ← ADD HERE ↓
def safe_hash(password: str) -> str:
    # bcrypt silently truncates at 72 bytes; passlib raises instead
    encoded = password.encode("utf-8")[:72]
    return pwd_context.hash(encoded.decode("utf-8", errors="ignore"))
# --------------------------------------------------
# Static Name/Area/Zipcode Data
# --------------------------------------------------

INDIAN_NAMES = [
    "Arjun Sharma", "Priya Nair", "Karthik Rajan", "Divya Menon", "Rahul Verma",
    "Sneha Iyer", "Vijay Kumar", "Ananya Pillai", "Suresh Babu", "Lakshmi Devi",
    "Manoj Pandey", "Kavitha Reddy", "Ravi Shankar", "Pooja Gupta", "Arun Krishnan",
    "Meera Nambiar", "Deepak Singh", "Nithya Venkat", "Harish Patel", "Saranya Mohan",
    "Ganesh Murthy", "Rekha Srinivasan", "Prasad Rao", "Anjali Das", "Naveen Pillai",
    "Sunita Joshi", "Vinod Nair", "Bhavana Raj", "Sanjay Mehta", "Lavanya Subramanian",
]

AREAS = {
    "Chennai":    ["Anna Nagar", "T Nagar", "Adyar", "Velachery", "Tambaram"],
    "Bangalore":  ["Koramangala", "Indiranagar", "Whitefield", "HSR Layout", "Jayanagar"],
    "Hyderabad":  ["Banjara Hills", "Jubilee Hills", "Madhapur", "Gachibowli", "Secunderabad"],
    "Coimbatore": ["RS Puram", "Gandhipuram", "Peelamedu", "Saibaba Colony", "Singanallur"],
    "Madurai":    ["Anna Nagar", "KK Nagar", "Tallakulam", "Iyer Bungalow", "Palanganatham"],
}

ZIPCODES = {
    "Chennai":    ["600001", "600002", "600020", "600042", "600045"],
    "Bangalore":  ["560001", "560008", "560066", "560034", "560011"],
    "Hyderabad":  ["500034", "500033", "500081", "500032", "500026"],
    "Coimbatore": ["641001", "641002", "641004", "641028", "641035"],
    "Madurai":    ["625001", "625002", "625003", "625010", "625020"],
}

DEFAULT_AREAS    = ["Main Street", "Cross Road", "Market Area", "Old Town", "New Layout"]
DEFAULT_ZIPCODES = ["500001", "600001", "700001", "800001", "900001"]


# --------------------------------------------------
# Load Master Data from DB
# --------------------------------------------------

def load_master_data(db: Session):
    try:
        banks = db.query(Bank).all()
        logger.info(f"Loaded {len(banks)} banks")
        if not banks:
            raise HTTPException(status_code=400, detail="No banks found. Please insert banks first.")

        branches = db.query(Branch).all()
        logger.info(f"Loaded {len(branches)} branches")
        if not branches:
            raise HTTPException(status_code=400, detail="No branches found. Please insert branches first.")

        cities = db.query(City).all()
        logger.info(f"Loaded {len(cities)} cities")
        if not cities:
            raise HTTPException(status_code=400, detail="No cities found. Please insert cities first.")

        return banks, branches, cities

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load master data: {e}")
        raise HTTPException(status_code=500, detail=f"Master data load failed: {str(e)}")


# --------------------------------------------------
# Main Simulation
# --------------------------------------------------

def run_simulation(
    db: Session,
    accounts: int,
    transfers_per_account: int,
    initial_deposit: int
):
    created_accounts = []
    account_bank_map = {}  # account_id -> (bank_id, branch_id)
    hashed_password = safe_hash("12345678")

    try:
        # Step 1: Load master data from DB
        banks, branches, cities = load_master_data(db)
        logger.info(f"Starting simulation: {accounts} accounts, {transfers_per_account} transfers each, deposit ₹{initial_deposit}")

        # Step 2: Create Users + Accounts
        for i in range(accounts):
            try:
                full_name  = random.choice(INDIAN_NAMES)
                first_name = full_name.split()[0].lower()

                city      = random.choice(cities)
                city_name = city.city_name
                area      = random.choice(AREAS.get(city_name, DEFAULT_AREAS))
                zipcode   = random.choice(ZIPCODES.get(city_name, DEFAULT_ZIPCODES))

                email = f"{first_name}.{uuid.uuid4().hex[:4]}@gmail.com"
                phone = str(random.randint(7000000000, 9999999999))

                user = User(
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    password_hash=hashed_password,
                    address_line=f"{random.randint(1, 99)}, {area} Street",
                    area=area,
                    zipcode=zipcode,
                    city_id=city.id,
                )
                db.add(user)
                db.flush()
                logger.info(f"[{i+1}/{accounts}] Created user: {full_name} (id={user.id})")

                bank   = random.choice(banks)
                branch = random.choice(branches)

                account = Account(
                    user_id=user.id,
                    account_number=str(random.randint(10000000000, 99999999999)),
                    account_type="savings",
                    status="active",
                    bank_id=bank.id,
                    branch_id=branch.id,
                )
                db.add(account)
                db.flush()
                logger.info(f"  Account: {account.account_number} | Bank: {bank.bank_name} | Branch: {branch.branch_name}")

                # Store bank/branch mapping for this account
                account_bank_map[account.id] = (bank.id, branch.id)

                deposit(
                    db,
                    account.id,
                    Decimal(initial_deposit),
                    bank_id=bank.id,
                    branch_id=branch.id
                )
                logger.info(f"  Deposited ₹{initial_deposit} to account {account.id}")

                created_accounts.append(account.id)

            except Exception as e:
                logger.error(f"Failed to create user/account at index {i}: {e}")
                raise HTTPException(status_code=500, detail=f"User/account creation failed at index {i}: {str(e)}")

        # Step 3: Random Transfers
        total_transfers = accounts * transfers_per_account
        executed        = 0
        skipped         = 0
        max_skips       = total_transfers * 3  # safety limit to avoid infinite loop

        logger.info(f"Starting {total_transfers} transfers...")

        while executed < total_transfers and skipped < max_skips:
            from_acc, to_acc = random.sample(created_accounts, 2)
            amount = Decimal(random.randint(10, 500))

            from_bank_id, from_branch_id = account_bank_map[from_acc]

            try:
                savepoint = db.begin_nested()

                transfer(
                    db,
                    from_acc,
                    to_acc,
                    amount,
                    idempotency_key=str(uuid.uuid4()),
                    bank_id=from_bank_id,
                    branch_id=from_branch_id
                )

                savepoint.commit()
                executed += 1
                logger.debug(f"Transfer {executed}/{total_transfers}: acc {from_acc} → acc {to_acc} ₹{amount}")

            except Exception as e:
                savepoint.rollback()
                skipped += 1
                logger.warning(f"Transfer skipped (acc {from_acc} → {to_acc}, ₹{amount}): {e}")

        if skipped >= max_skips:
            logger.warning(f"Reached max skip limit ({max_skips}). Stopped transfers early.")

        # Step 4: Final Commit
        db.commit()
        logger.info(f"Simulation complete. Accounts: {accounts}, Executed: {executed}, Skipped: {skipped}")

        return {
            "accounts_created": accounts,
            "transfers_executed": executed,
            "transfers_skipped": skipped,
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")