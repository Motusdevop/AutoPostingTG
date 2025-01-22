# from typing import List
#
# from pydantic import BaseModel, ConfigDict
#
#
# class NewChannel(BaseModel):
#     name: str
#     share_link: str | None
#     chat_id: int | None
#     parse_mode: str | None
#     interval: int | None
#
#
# class Channel(NewChannel):
#     id: int
#     path_to_source_dir: str
#     path_to_done_dir: str
#     path_to_except_dir: str
#
#     model_config = ConfigDict(from_attributes=True)
#
#
# class Channels(BaseModel):
#     channels: List[Channel]

from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

class NewChannel(BaseModel):
    name: str = Field(..., example="TechUpdatesChannel")
    chat_id: Optional[int] = Field(None, example=123456789)
    parse_mode: Optional[str] = Field(None, example="Markdown")
    interval: Optional[int] = Field(None, example=60)

    class Config:
        schema_extra = {
            "example": {
                "name": "TechUpdatesChannel",
                "chat_id": 123456789,
                "parse_mode": "Markdown",
                "interval": 60
            }
        }


class Channel(NewChannel):
    id: int = Field(..., example=1)
    path_to_source_dir: str = Field(..., example="/channels/TechUpdatesChannel/source")
    path_to_done_dir: str = Field(..., example="/channels/TechUpdatesChannel/done")
    path_to_except_dir: str = Field(..., example="/channels/TechUpdatesChannel/except")

    active: bool = Field(..., example=False)

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "TechUpdatesChannel",
                "chat_id": 123456789,
                "parse_mode": "Markdown",
                "interval": 60,
                "path_to_source_dir": "/channels/TechUpdatesChannel/source",
                "path_to_done_dir": "/channels/TechUpdatesChannel/done",
                "path_to_except_dir": "/channels/TechUpdatesChannel/except"
            }
        }


class Channels(BaseModel):
    channels: List[Channel]

    class Config:
        schema_extra = {
            "example": {
                "channels": [
                    {
                        "id": 1,
                        "name": "TechUpdatesChannel",
                        "share_link": "https://t.me/TechUpdatesChannel",
                        "chat_id": 123456789,
                        "parse_mode": "Markdown",
                        "interval": 60,
                        "path_to_source_dir": "/channels/TechUpdatesChannel/source",
                        "path_to_done_dir": "/channels/TechUpdatesChannel/done",
                        "path_to_except_dir": "/channels/TechUpdatesChannel/except"
                    },
                    {
                        "id": 2,
                        "name": "NewsChannel",
                        "share_link": "https://t.me/NewsChannel",
                        "chat_id": 987654321,
                        "parse_mode": "HTML",
                        "interval": 120,
                        "path_to_source_dir": "/channels/NewsChannel/source",
                        "path_to_done_dir": "/channels/NewsChannel/done",
                        "path_to_except_dir": "/channels/NewsChannel/except"
                    }
                ]
            }
        }
