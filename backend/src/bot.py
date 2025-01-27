import asyncio
from typing import List

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, InputMediaPhoto
from loguru import logger

from settings import get_settings


class CustomBot(Bot):
    def __init__(self, *args, **kwargs):

        cfg = get_settings()
        token = cfg.bot_token
        default = DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
        super().__init__(token, default=default, *args, **kwargs)
        logger.success("bot created successfully")

    async def send_post(self, channel_id: int | str, media: List[InputMediaPhoto]):
        logger.info("Sending post to channel")
        await self.send_media_group(channel_id, media=media)
        await self.session.close()
        logger.info("Post send successfully")
        return True

if __name__ == "__main__":
    bot = CustomBot()

    print(asyncio.run(bot.get_channels_chat_id("@testing_autopost")))
