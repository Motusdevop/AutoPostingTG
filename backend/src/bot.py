import asyncio
from typing import List

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, InputMediaPhoto, FSInputFile

from settings import Settings, get_settings

from loguru import logger


class CustomBot(Bot):
    def __init__(self, *args, **kwargs):

        cfg = get_settings()
        token = cfg.bot_token
        default = DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
        super().__init__(token, default=default, *args, **kwargs)
        logger.success('bot created successfully')

    async def send_post(self, channel_id: int | str, media: List[InputMediaPhoto]):
        logger.info('Sending post to channel')
        try:
            await self.send_media_group(channel_id, media=media)
            await self.session.close()
            logger.info('Post send successfully')
            return True

        except Exception as e:
            logger.error(e)

    async def get_channels_chat_id(self, channel_id: int | str):
        logger.info('Getting channel chat id')
        try:
            chat_full_info = await self.get_chat(chat_id=channel_id)
            logger.success('Get channel chat id successfully')
            await bot.session.close()
            return chat_full_info.id
        except Exception as e:
            logger.error(e)

if __name__ == '__main__':
    bot = CustomBot()

    print(asyncio.run(bot.get_channels_chat_id('@testing_autopost')))
