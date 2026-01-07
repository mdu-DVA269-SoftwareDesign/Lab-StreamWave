from pydantic import BaseModel, Field, computed_field
from typing import Optional


class MediaContent(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    title: Optional[str] = None
    url: Optional[str] = None
    length: Optional[int] = None
    genre: Optional[str] = None
    cover_image: Optional[str] = None
    artist: Optional[str] = None

    @computed_field
    def media_type(self) -> str:
        return self.__class__.__name__

    class Config:
        populate_by_name = True
