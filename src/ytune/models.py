
from pydantic import BaseModel, ConfigDict, Field


class Track(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    video_id: str = Field(..., alias="videoId")
    title: str
    artist: str
    album: str | None = None
    duration: str | None = None
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")

class Album(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    album_id: str = Field(..., alias="browseId")
    title: str
    artist: str
    year: str | None = None
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")

class Playlist(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    playlist_id: str = Field(..., alias="playlistId")
    title: str
    count: int | None = None
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")
