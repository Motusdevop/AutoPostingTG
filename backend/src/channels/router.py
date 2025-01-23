import os

import aiogram.exceptions
from aiogram.enums import ChatMemberStatus
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from auth.tools import authenticate_user
from bot import CustomBot
from channels.schemas import Channel, Channels, NewChannel
from channels_files import ChannelExists, ChannelsFileManager
from models import ChannelORM
from repository import ChannelRepository
from scheduler import add_posting_task, deactivate_channel
from settings import Settings, get_settings

router = APIRouter(prefix="/channels", tags=["channels"])

cfg: Settings = get_settings()


@router.get("/get_all")
async def get_all(authorized: bool = Depends(authenticate_user)) -> Channels:
    if not authorized:
        logger.warning("Unauthorized access attempt for /get_all")
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        res = ChannelRepository.get_all()
        channels = [Channel.model_validate(x.__dict__) for x in res]
        logger.info("Fetched all channels successfully")
        return Channels(channels=channels)
    except Exception as e:
        logger.error(f"Error fetching channels: {e}")
        raise HTTPException(status_code=500, detail="Error fetching channels")


@router.get("/get/{id}")
async def get_by_id(
    id: int, authorized: bool = Depends(authenticate_user)
) -> Channel | None:
    if not authorized:
        logger.warning(f"Unauthorized access attempt for /get/{id}")
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        channel: ChannelORM = ChannelRepository.get(id)
        if not channel:
            logger.warning(f"Channel with ID {id} not found")
            return None
        logger.info(f"Channel with ID {id} fetched successfully")
        return Channel.model_validate(channel.__dict__)
    except Exception as e:
        logger.error(f"Error fetching channel {id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching channel {id}")


@router.post("/add")
async def add_channel(
    channel: NewChannel, authorized: bool = Depends(authenticate_user)
):
    if not authorized:
        logger.warning("Unauthorized access attempt for /add")
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        filemanager = ChannelsFileManager(base_dir=cfg.base_dir)

        if ChannelRepository.check_exist(channel.name):
            logger.error(f"Channel with name '{channel.name}' already exists")
            raise ChannelExists(f"Channel '{channel.name}' already exists")

        filemanager.create_channel(channel.name)
        data = channel.model_dump()
        data["active"] = False
        data["path_to_source_dir"] = os.path.join(cfg.base_dir, data["name"], "source")
        data["path_to_except_dir"] = os.path.join(cfg.base_dir, data["name"], "except")
        data["path_to_done_dir"] = os.path.join(cfg.base_dir, data["name"], "done")

        ChannelRepository.add(ChannelORM(**data))
        logger.info(f"Channel '{channel.name}' created successfully")
        return {"status": "ok"}

    except ChannelExists as e:
        logger.warning(f"Channel creation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error creating channel '{channel.name}': {e}")
        raise HTTPException(
            status_code=500, detail=f"Error creating channel '{channel.name}'"
        )


@router.delete("/delete/{id}")
async def delete_channel(id: int, authorized: bool = Depends(authenticate_user)):
    if not authorized:
        logger.warning(f"Unauthorized access attempt for /delete/{id}")
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        channel = ChannelRepository.get(id)
        if not channel:
            logger.warning(f"Channel with ID {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Channel not found")

        channel_name = channel.name
        ChannelRepository.delete(id)

        filemanager = ChannelsFileManager(base_dir=cfg.base_dir)
        filemanager.delete_channel(channel_name=channel_name)

        logger.info(f"Channel '{channel_name}' deleted successfully")
        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error deleting channel {id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting channel {id}")


@router.put("/update/{id}")
async def update_channel(
    id: int, channel: NewChannel, authorized: bool = Depends(authenticate_user)
) -> dict:
    if not authorized:
        logger.warning(f"Unauthorized access attempt for /update/{id}")
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        data = channel.model_dump()
        existing_channel: ChannelORM = ChannelRepository.get(id)

        if existing_channel.active:
            deactivate_channel(existing_channel)
            data["active"] = False

        data["id"] = id
        data["path_to_source_dir"] = existing_channel.path_to_source_dir
        data["path_to_except_dir"] = existing_channel.path_to_except_dir
        data["path_to_done_dir"] = existing_channel.path_to_done_dir
        data["active"] = False

        if not existing_channel:
            logger.warning(f"Channel with ID {id} not found for update")
            raise HTTPException(status_code=404, detail="Channel not found")

        ChannelRepository.update(ChannelORM(**data))
        logger.info(f"Channel with ID {id} updated successfully")
        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error updating channel {id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating channel {id}")


@router.post("/on/{id}")
async def on_channel(id: int, authorized: bool = Depends(authenticate_user)):
    if not authorized:
        logger.warning(f"Unauthorized access attempt for /on/{id}")
        raise HTTPException(status_code=401, detail="Unauthorized")
    else:
        try:
            channel: ChannelORM = ChannelRepository.get(id)
            if channel:
                channel.active = True
                ChannelRepository.update(channel)
                add_posting_task(channel)
            else:
                raise HTTPException(status_code=404, detail="Channel not found")

        except Exception as e:
            logger.error(f"Error updating channel {id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error updating channel {id}")


@router.post("/off/{id}")
async def off_channel(id: int, authorized: bool = Depends(authenticate_user)):
    if not authorized:
        logger.warning(f"Unauthorized access attempt for /off/{id}")
        raise HTTPException(status_code=401, detail="Unauthorized")
    else:
        try:
            channel: ChannelORM = ChannelRepository.get(id)
            if channel:
                channel: ChannelORM = ChannelRepository.get(id)
                deactivate_channel(channel)
            else:
                raise HTTPException(status_code=404, detail="Channel not found")

        except Exception as e:
            logger.error(f"Error updating channel {id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error updating channel {id}")


@router.post("/check/{chat_id}")
async def check(chat_id: int, authorized: bool = Depends(authenticate_user)):
    if not authorized:
        logger.warning(f"Unauthorized access attempt for /check/{chat_id}")
        raise HTTPException(status_code=401, detail="Unauthorized")
    else:
        try:
            bot = CustomBot()
            # Получаем информацию о члене чата (в данном случае о боте)
            chat_member = await bot.get_chat_member(chat_id, bot.id)
            status = chat_member.status
            await bot.session.close()

            # Проверяем, имеет ли бот право на отправку сообщений
            if status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
                return True
            else:
                return False
        except aiogram.exceptions.TelegramBadRequest as e:
            logger.error(f"Not found chat {chat_id}")
            return False

        # except Exception as e:
        #     logger.error(f"Error check channel {chat_id}: {e}")
        #     raise HTTPException(status_code=500, detail=f"Error check permissions {chat_id}")
