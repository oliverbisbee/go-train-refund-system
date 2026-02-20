from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.db.session import engine
from app.db.base_class import Base
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.delay_detector import DelayDetector
from app.db.session import SessionLocal

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GO Train Refund System")

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


# Background scheduler for polling GTFS feed
def check_delays_job():
    """Background job to check for delays"""
    db = SessionLocal()
    try:
        detector = DelayDetector(db)
        detector.check_delays_for_subscriptions()
    finally:
        db.close()


scheduler = BackgroundScheduler()
scheduler.add_job(check_delays_job, 'interval', minutes=1)  # Run every 1 minute


@app.on_event("startup")
def startup_event():
    scheduler.start()
    print("🚂 GO Train Refund System Started")
    print("📊 Background delay checker running every 1 minute")


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


@app.get("/")
def root():
    return {"message": "GO Train Refund System API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}