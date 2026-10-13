from fastapi import FastAPI

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.tickets import router as tickets_router

app = FastAPI(
    title="Support Intelligence API",
    version="0.1.0",
)


app.include_router(tickets_router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {"message": "Support Intelligence API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
