import os

from loguru import logger


class ChannelExists(Exception):
    pass


class ChannelNotFound(Exception):
    pass


class ChannelBroken(Exception):
    pass


class ChannelsFileManager:
    _instance = None

    def __init__(self, base_dir="/"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            logger.error(f"Base directory does not exist: {self.base_dir}")
            raise FileNotFoundError(f"Base directory {self.base_dir} not found.")

    def get_channels(self):
        try:
            channels = os.listdir(self.base_dir)
            data = {"channels": []}
            for channel in channels:
                if os.path.isdir(os.path.join(self.base_dir, channel)):
                    data["channels"].append(self.get_channel_by_name(channel))
            logger.info(f"Retrieved channels: {data}")
            return data
        except Exception as e:
            logger.error(f"Failed to retrieve channels: {e}")
            return None

    def get_channel_by_name(self, name):
        dirs = ["source", "except", "done"]
        data = {name: {}}
        if os.path.exists(os.path.join(self.base_dir, name)):
            try:
                for dir in dirs:
                    dir_path = os.path.join(self.base_dir, name, dir)
                    if os.path.exists(dir_path):
                        data[name][dir] = os.listdir(dir_path)
                    else:
                        # Если директория не существует, вызываем fix_channel для восстановления структуры
                        logger.warning(
                            f"Directory {dir_path} does not exist, fixing..."
                        )
                        # Если директория не существует, возвращаем пустой список
                        logger.info(f"Directory {dir_path} not found")
                        raise ChannelBroken(f"Directory {dir_path} not found")
                logger.info(f"Retrieved data for channel: {name}")
                return data
            except FileNotFoundError as e:
                logger.error(f"Channel {name} not found: {e}")
                raise ChannelNotFound(f"Channel {name} not found")
            except Exception as e:
                logger.error(f"Failed to retrieve channel {name}: {e}")
                return None
        else:
            raise ChannelNotFound(f"Channel {name} not found")

    def create_channel(self, channel_name: str):
        """Создает структуру канала с подкаталогами 'source', 'except' и 'done'."""
        try:
            channel_path = os.path.join(self.base_dir, channel_name)

            # Проверяем, существует ли уже канал
            if os.path.exists(channel_path):
                logger.warning(f"Channel {channel_name} already exists.")
                raise ChannelExists(f"Channel {channel_name} already exists.")

            # Создаем канал
            os.makedirs(channel_path)
            logger.info(f"Created channel: {channel_path}")

            # Создаем подкаталоги для канала
            for subdir in ["source", "except", "done"]:
                subdir_path = os.path.join(channel_path, subdir)
                os.makedirs(subdir_path)
                logger.info(f"Created subdirectory: {subdir_path}")

        except ChannelExists as e:
            logger.error(f"Channel creation failed: {e}")
        except Exception as e:
            logger.error(f"Failed to create channel {channel_name}: {e}")

    def delete_channel(self, channel_name: str):
        """Удаляет канал и его структуру (subdirectories)."""
        try:
            channel_path = os.path.join(self.base_dir, channel_name)

            # Проверяем, существует ли канал
            if not os.path.exists(channel_path):
                logger.error(f"Channel {channel_name} does not exist.")
                raise ChannelNotFound(f"Channel {channel_name} does not exist.")

            # Удаляем подкаталоги канала
            for subdir in ["source", "except", "done"]:
                subdir_path = os.path.join(channel_path, subdir)
                if os.path.exists(subdir_path):
                    files = os.listdir(subdir_path)
                    for file in files:
                        file_path = os.path.join(subdir_path, file)
                        os.remove(file_path)
                        logger.info(f"Deleted file: {file_path}")
                    os.rmdir(subdir_path)
                    logger.info(f"Removed subdirectory: {subdir_path}")

            # Удаляем сам канал
            os.rmdir(channel_path)
            logger.info(f"Removed channel: {channel_name}")
        except ChannelNotFound as e:
            logger.error(f"Failed to delete channel {channel_name}: {e}")
        except Exception as e:
            logger.error(
                f"An error occurred while deleting channel {channel_name}: {e}"
            )

    def fix_channel(self, channel_name: str, missing_dir: str):
        """Восстанавливает недостающий подкаталог для канала."""
        try:
            channel_path = os.path.join(self.base_dir, channel_name)
            if not os.path.exists(channel_path):
                logger.error(
                    f"Channel {channel_name} does not exist. Cannot fix missing subdirectory."
                )
                raise ChannelNotFound(f"Channel {channel_name} does not exist.")

            # Восстанавливаем недостающий подкаталог
            missing_dir_path = os.path.join(channel_path, missing_dir)
            os.makedirs(missing_dir_path)
            logger.info(f"Created missing directory: {missing_dir_path}")

        except ChannelNotFound as e:
            logger.error(f"Failed to fix channel {channel_name}: {e}")
        except Exception as e:
            logger.error(f"An error occurred while fixing channel {channel_name}: {e}")

    def clear_all_channels(self):
        """Удаляет все каналы и их структуру."""
        try:
            channels = os.listdir(self.base_dir)
            for channel in channels:
                if os.path.isdir(os.path.join(self.base_dir, channel)):
                    self.delete_channel(channel)
            logger.info("Successfully cleared all channels.")
        except Exception as e:
            logger.error(f"Failed to clear all channels: {e}")


if __name__ == "__main__":
    manager = ChannelsFileManager(base_dir="../channels")

    # Создание нового канала
    manager.create_channel("new_channel")

    # Получение всех каналов
    channels_data = manager.get_channels()
    print(channels_data)
