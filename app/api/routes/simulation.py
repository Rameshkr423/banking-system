from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.simulation import SimulationRequest
from app.services.simulation_service import run_simulation
from app.services.transaction_service import deposit, get_balance, withdraw,transfer

router = APIRouter()

@router.post("/simulate")
def simulate_data(request: SimulationRequest, db: Session = Depends(get_db)):

    result = run_simulation(
        db,
        request.accounts,
        request.transfers_per_account,
        request.initial_deposit
    )

    return result