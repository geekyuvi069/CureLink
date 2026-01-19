from fastapi import FastAPI
from app.core.config import settings
from app.api.chat import router as chat_router
from app.api.slack import router as slack_router


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Agentic AI Doctor Appointment & Reporting System API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router, prefix="/api")
app.include_router(slack_router, prefix="/api/slack")

@app.get("/")
async def root():
    return {"message": "Welcome to the Doctor Appointment System API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
