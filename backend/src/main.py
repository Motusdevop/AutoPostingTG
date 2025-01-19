import ftplib
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from settings import Settings, get_settings

from loguru import logger

from bot import CustomBot, InputMediaPhoto, FSInputFile

from channels.router import router as channels_router
from database import create_tables, drop_tables

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

# Параметры FTP-сервера
FTP_HOST = "localhost"
FTP_PORT = 21
FTP_USER = "user"
FTP_PASS = "password"

@app.post("/upload/")
async def upload_to_ftp(file: UploadFile = File(...)):
    # Подключение к FTP серверу
    with ftplib.FTP() as ftp:
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)

        # Загрузка файла на FTP сервер
        with ftp.open(f"/home/ftpusers/user/{file.filename}", "wb") as f:
            content = await file.read()
            f.write(content)

    return {"filename": file.filename}


@app.get('/ping')
async def ping():
    logger.info("posting...")
    bot = CustomBot()

    text = """
*Таким* образом новая модель `организационной деятельности` в значительной степени обуславливает создание соответствующий условий активизации. Равным образом сложившаяся структура организации в значительной степени обуславливает создание форм развития. Товарищи! реализация намеченных плановых заданий представляет собой интересный эксперимент проверки новых предложений. Товарищи! начало повседневной работы по формированию позиции влечет за собой процесс внедрения и модернизации модели развития.

Повседневная практика показывает, что постоянный количественный рост и сфера нашей активности позволяет оценить значение системы обучения кадров, соответствует насущным потребностям. Значимость этих проблем настолько очевидна, что консультация с широким активом играет важную роль в формировании модели развития.
    """

    media = [InputMediaPhoto(media=FSInputFile('assets/img_1.png'), caption=text)]

    await bot.send_post('@testing_autopost', media=media)
    logger.info("post finished")

    media = [InputMediaPhoto(media=FSInputFile('assets/img_1.png'), caption=text),
             InputMediaPhoto(media=FSInputFile('assets/img_2.png'))]

    await bot.send_post('@testing_autopost', media=media)
    logger.info("post finished")

    media = [InputMediaPhoto(media=FSInputFile('assets/img_1.png'), caption=text),
             InputMediaPhoto(media=FSInputFile('assets/img_2.png')),
             InputMediaPhoto(media=FSInputFile('assets/img_3.png'))]

    await bot.send_post('@testing_autopost', media=media)
    logger.success("post finished")

    return {'status': True}


if __name__ == '__main__':
    uvicorn.run(app)
