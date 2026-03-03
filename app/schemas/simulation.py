from pydantic import BaseModel

class SimulationRequest(BaseModel):
    accounts: int
    transfers_per_account: int
    initial_deposit: int