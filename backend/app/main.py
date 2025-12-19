from fastapi import FastAPI
from .api.endpoints import router
from .core.config import settings
from .db.mongodb import db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .services.monitor_service import monitor_service

app = FastAPI(title=settings.PROJECT_NAME)
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_db_client():
    await db.connect_to_database()
    
    # Start Scheduler
    scheduler.add_job(monitor_service.check_pending_instances, "interval", seconds=30)
    scheduler.add_job(monitor_service.auto_replenish, "interval", minutes=5)
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_db_client():
    await db.close_database_connection()
    scheduler.shutdown()

app.include_router(router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "RentMachine API is running"}
