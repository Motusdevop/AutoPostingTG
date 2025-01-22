import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from loguru import logger

from bot import CustomBot, FSInputFile, InputMediaPhoto
from channels.router import router as channels_router
from channels_files import ChannelsFileManager
from database import create_tables, drop_tables
from settings import Settings, get_settings
from channels_files import ChannelsFileManager
from scheduler import scheduler, add_tasks

cfg: Settings = get_settings()

logger.add(cfg.logs_path + '/' + 'loguru.log', rotation="5 hours", retention=3)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    logger.success("Tables created")
    scheduler.start()
    await add_tasks()
    logger.success("Scheduler started...")

    yield

    scheduler.shutdown()
    logger.success("Scheduler stopped")
    if cfg.debug:
        drop_tables()
        filemanager = ChannelsFileManager(cfg.base_dir)
        filemanager.clear_all_channels()
        logger.critical("Tables dropped")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
CORSMiddleware,
allow_origins=["*"], # Allows all origins
allow_credentials=True,
allow_methods=["*"], # Allows all methods
allow_headers=["*"], # Allows all headers
)

logger.success("Application created")

app.include_router(channels_router)


@app.get("/ping")
async def ping():
    logger.info("ping")

    return {"status": True}


if __name__ == "__main__":
    uvicorn.run(app)
