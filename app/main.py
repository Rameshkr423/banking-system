from fastapi import FastAPI
from app.api.routes import user
from app.api.routes import transaction
from app.core.config import settings
from app.db.init_db import init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0"
)


@app.on_event("startup")
def on_startup():
    # Initialize database tables (development only)
    init_db()


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "healthy"}


# Routers
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(transaction.router, prefix="/transactions", tags=["Transactions"])
