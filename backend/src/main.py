from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from loguru import logger

from bot import CustomBot, FSInputFile, InputMediaPhoto
from channels.router import router as channels_router
from channels_files import ChannelsFileManager
from database import create_tables
from settings import Settings, get_settings

cfg: Settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    logger.success("Tables created")
    yield
    # Clean up the ML models and release the resources
    logger.critical("Tables dropped")


app = FastAPI(lifespan=lifespan)
logger.success("Application created")

app.include_router(channels_router)


@app.get("/ping")
async def ping():
    logger.info("posting...")
    bot = CustomBot()

    text = """
*Таким* образом новая модель `организационной деятельности` в значительной степени обуславливает создание соответствующий условий активизации. Равным образом сложившаяся структура организации в значительной степени обуславливает создание форм развития. Товарищи! реализация намеченных плановых заданий представляет собой интересный эксперимент проверки новых предложений. Товарищи! начало повседневной работы по формированию позиции влечет за собой процесс внедрения и модернизации модели развития.

Повседневная практика показывает, что постоянный количественный рост и сфера нашей активности позволяет оценить значение системы обучения кадров, соответствует насущным потребностям. Значимость этих проблем настолько очевидна, что консультация с широким активом играет важную роль в формировании модели развития.
    """

    media = [InputMediaPhoto(media=FSInputFile("assets/img_1.png"), caption=text)]

    await bot.send_post("@testing_autopost", media=media)
    logger.info("post finished")

    media = [
        InputMediaPhoto(media=FSInputFile("assets/img_1.png"), caption=text),
        InputMediaPhoto(media=FSInputFile("assets/img_2.png")),
    ]

    await bot.send_post("@testing_autopost", media=media)
    logger.info("post finished")

    media = [
        InputMediaPhoto(media=FSInputFile("assets/img_1.png"), caption=text),
        InputMediaPhoto(media=FSInputFile("assets/img_2.png")),
        InputMediaPhoto(media=FSInputFile("assets/img_3.png")),
    ]

    await bot.send_post("@testing_autopost", media=media)
    logger.success("post finished")

    return {"status": True}


@app.get("/files")
async def files():
    filemanager = ChannelsFileManager(base_dir="../channels")
    filemanager.create_channel("new_channel")
    return filemanager.get_channels()


if __name__ == "__main__":
    uvicorn.run(app)
