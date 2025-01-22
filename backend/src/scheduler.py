import os
import shutil
from datetime import datetime
from typing import List, Dict

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from PIL import Image
from io import BytesIO

from models import ChannelORM
from repository import ChannelRepository
from channels_files import ChannelsFileManager, ChannelNotFound, ChannelBroken
from settings import get_settings, Settings
from bot import CustomBot, FSInputFile, InputMediaPhoto

scheduler = AsyncIOScheduler()
cfg: Settings = get_settings()


async def add_tasks():
    """Добавление задач для всех активных каналов"""
    active_channels = ChannelRepository.get_actives()

    if not active_channels:
        logger.info("No active channels found.")

    for channel in active_channels:
        add_posting_task(channel)


def add_posting_task(channel: ChannelORM):
    """Добавление задачи на постинг для конкретного канала"""
    logger.info(f"Adding posting task for channel {channel.name} (ID: {channel.id})")

    scheduler.add_job(
        posting,
        trigger=IntervalTrigger(seconds=5, start_date=datetime.now()),
        id=str(channel.id),
        name=channel.name,
        args=[channel],
        replace_existing=True
    )


async def posting(channel: ChannelORM):
    """Функция, которая выполняет постинг для конкретного канала"""
    logger.info(f"Start posting process for channel {channel.name} (ID: {channel.id})")

    filemanager = ChannelsFileManager(base_dir=cfg.base_dir)

    try:
        files = filemanager.get_channel_by_name(channel.name)
        source_files = files[channel.name]['source']

        if not source_files:
            logger.info(f"No source files to post for channel {channel.name}")
            deactivate_channel(channel)
            return

        source_files.sort()  # Сортировка по имени файлов

        # Группируем файлы по номеру
        file_groups = group_files_by_number(source_files)
        for file_number, file_group in file_groups.items():
            try:
                txt_files, jpg_files = separate_files_by_type(file_group)

                # Публикуем только если есть хотя бы один .txt файл
                if not txt_files:
                    logger.warning(f"No .txt file found for {file_number} in channel {channel.name}")
                    move_files_to_except(channel, jpg_files)
                    continue

                # Публикуем комплект файлов
                publication_files = prepare_publication_files(txt_files, jpg_files)
                await publish_files(channel, publication_files)

                logger.info(f"Successfully published {file_number} in channel {channel.name}")

            except Exception as e:
                logger.error(f"Error processing file group {file_number} in channel {channel.name}: {e}")

    except ChannelNotFound as e:
        handle_channel_not_found(channel, e)

    except ChannelBroken as e:
        await handle_channel_broken(channel, e)

    except Exception as e:
        logger.error(f"Unexpected error in posting for channel {channel.name}: {e}")


def group_files_by_number(files: List[str]) -> Dict[str, List[str]]:
    """Группируем файлы по числовому идентификатору (например, 0001, 0035)"""
    file_groups = {}

    for file in files:
        # Извлекаем базовый номер (до подчеркивания или точки)
        base_number = file.split('.')[0].split('_')[0]

        if base_number not in file_groups:
            file_groups[base_number] = []

        file_groups[base_number].append(file)

    logger.debug(f"Grouped files: {file_groups}")
    return file_groups


def separate_files_by_type(file_group: List[str]) -> (List[str], List[str]):
    """Разделяем файлы на текстовые (.txt) и изображения (.jpg)"""
    txt_files = [f for f in file_group if f.endswith('.txt')]
    jpg_files = [f for f in file_group if f.endswith('.jpg')]


    logger.debug(f"Separated files: {len(txt_files)} .txt files, {len(jpg_files)} .jpg files")
    return txt_files, jpg_files


def prepare_publication_files(txt_files: List[str], jpg_files: List[str]) -> List[str]:
    """Подготовка списка файлов для публикации (ограничиваем до 3 изображений)"""
    # Сортируем jpg файлы по имени и берем только первые 3
    jpg_files.sort()
    jpg_files = jpg_files[:3]

    # Формируем список для публикации (1 txt + до 3 jpg)
    publication_files = txt_files + jpg_files
    logger.debug(f"Prepared publication files: {publication_files}")
    return publication_files


async def publish_files(channel: ChannelORM, files: List[str]):
    """Логика публикации файлов в канал"""
    logger.info(f"Publishing files {files} to channel {channel.name}")

    bot = CustomBot()
    try:
        # Открываем текстовый файл для публикации
        txt_file = next((f for f in files if f.endswith('.txt')), None)
        if txt_file:
            txt_path = os.path.join(cfg.base_dir, channel.name, 'source', txt_file)
            with open(txt_path, 'r') as f:
                text = f.read()

            # Если есть изображения, добавляем их
            jpg_files = [f for f in files if f.endswith('.jpg')]
            media = []

            for file in jpg_files:
                file_path = os.path.join(cfg.base_dir, channel.name, 'source', file)

                # Если размер изображения больше 5 МБ, уменьшаем его
                if os.path.getsize(file_path) > 5 * 1024 * 1024:  # больше 5 МБ
                    file_path = await compress_image(file_path)  # уменьшаем изображение

                media.append(InputMediaPhoto(media=FSInputFile(file_path), caption=text))

            if media:
                await bot.send_post(channel.chat_id, media=media)
            else:
                await bot.send_message(channel.chat_id, text=text, parse_mode=channel.parse_mode)

            # Закрываем сессию после отправки
            await bot.session.close()

            # Если публикация прошла успешно, перемещаем файлы в папку done
            move_files_to_done(channel, files)

            logger.info(f"Successfully published message for {channel.name}")

        else:
            logger.warning(f"No .txt file found for channel {channel.name}")
            # Если нет .txt файла, перемещаем файлы в папку except
            move_files_to_except(channel, files)

    except Exception as e:
        logger.error(f"Failed to publish files for {channel.name}: {e}")
        # В случае ошибки, перемещаем файлы в папку except
        move_files_to_except(channel, files)

    finally:
        # Закрываем сессию бота в любом случае
        await bot.session.close()


async def compress_image(file_path: str) -> str:
    """Сжимаем изображение, если его размер больше 5 МБ"""
    logger.info(f"Compressing image: {file_path}")

    # Открываем изображение
    with Image.open(file_path) as img:
        # Сохраняем оригинальные параметры изображения
        original_width, original_height = img.size
        logger.info(f"Original image size: {original_width}x{original_height}")

        # Понижаем качество изображения, если оно слишком большое
        new_file_path = file_path.replace('source', 'temp')
        if img.mode in ("RGBA", "P"):  # Преобразуем изображения в RGB, если они с альфа-каналом
            img = img.convert("RGB")

        # Уменьшаем размер изображения пропорционально
        max_size = (1920, 1920)  # Устанавливаем максимальные размеры
        img.thumbnail(max_size, Image.ANTIALIAS)

        # Сохраняем изображение с качеством 85% для уменьшения размера файла
        img.save(new_file_path, format="JPEG", quality=85)

        # Проверяем размер файла, если он меньше 5 MB, оставляем его, иначе пробуем еще раз с меньшим качеством
        while os.path.getsize(new_file_path) > 5 * 1024 * 1024:  # Если больше 5 МБ
            quality = 75
            img.save(new_file_path, format="JPEG", quality=quality)
            quality -= 5
            if quality < 50:
                logger.warning(f"Unable to compress {file_path} under 5MB")
                break

        logger.info(f"Compressed image saved to: {new_file_path}, new size: {os.path.getsize(new_file_path) / 1024 / 1024:.2f} MB")
        return new_file_path


def move_files_to_done(channel: ChannelORM, files: List[str]):
    """Перемещаем файлы в папку done"""
    logger.info(f"Moving files to 'done' for channel {channel.name}")

    for file in files:
        source_path = os.path.join(cfg.base_dir, channel.name, 'source', file)
        done_path = os.path.join(cfg.base_dir, channel.name, 'done', file)

        try:
            shutil.move(source_path, done_path)
            logger.info(f"File {file} moved to 'done' for channel {channel.name}")
        except Exception as e:
            logger.error(f"Failed to move file {file} to 'done': {e}")


def move_files_to_except(channel: ChannelORM, files: List[str]):
    """Перемещаем файлы в папку except"""
    logger.info(f"Moving files to 'except' for channel {channel.name}")

    for file in files:
        source_path = os.path.join(cfg.base_dir, channel.name, 'source', file)
        except_path = os.path.join(cfg.base_dir, channel.name, 'except', file)

        try:
            shutil.move(source_path, except_path)
            logger.info(f"File {file} moved to 'except' for channel {channel.name}")
        except Exception as e:
            logger.error(f"Failed to move file {file} to 'except': {e}")


def deactivate_channel(channel: ChannelORM):
    """Деактивируем канал, если нет файлов для публикации"""
    logger.info(f"Deactivating channel {channel.name} (ID: {channel.id})")
    channel.active = False
    ChannelRepository.update(channel)
    scheduler.remove_job(str(channel.id))


def handle_channel_not_found(channel: ChannelORM, exception: ChannelNotFound):
    """Обработка ошибки: канал не найден"""
    logger.error(f"Channel {channel.name} not found: {exception}")
    filemanager = ChannelsFileManager(base_dir=cfg.base_dir)
    filemanager.create_channel(channel.name)
    scheduler.remove_job(str(channel.id))
    deactivate_channel(channel)


async def handle_channel_broken(channel: ChannelORM, exception: ChannelBroken):
    """Обработка ошибки: канал поврежден"""
    logger.warning(f"Channel {channel.name} is broken: {exception}")
    filemanager = ChannelsFileManager(base_dir=cfg.base_dir)
    filemanager.fix_channel(channel.name)
    await posting(channel)  # Попробуем снова выполнить постинг