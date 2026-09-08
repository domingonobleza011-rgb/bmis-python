from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import engine, Base
from . import models  # noqa: F401 - registers models on Base
from .routers import auth, residents, staff, complaints, messages, announcements, youth, dashboard
from .routers.certificates import certificate_routers

app = FastAPI(title="BMIS Barangay San Pedro API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup if they don't exist yet (schema.sql is the
# source of truth for a fresh deploy; this just keeps dev in sync)
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(residents.router)
app.include_router(staff.router)
app.include_router(complaints.router)
app.include_router(messages.router)
app.include_router(announcements.router)
app.include_router(youth.router)
app.include_router(dashboard.router)
for r in certificate_routers:
    app.include_router(r)

app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.get("/api/health")
def health():
    return {"status": "ok"}
