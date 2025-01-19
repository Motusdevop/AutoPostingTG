from typing import List

from pydantic import BaseModel, ConfigDict


class NewChannel(BaseModel):
    name: str
    share_link: str | None
    chat_id: int | None
    parse_mode: str | None
    interval: int | None


class Channel(NewChannel):
    id: int
    path_to_source_dir: str
    path_to_done_dir: str
    path_to_except_dir: str

    model_config = ConfigDict(from_attributes=True)


class Channels(BaseModel):
    channels: List[Channel]
