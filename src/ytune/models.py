from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class Track(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    video_id: str = Field(..., alias="videoId")
    title: str
    artist: str
    album: Optional[str] = None
    duration: Optional[str] = None
    thumbnail_url: Optional[str] = Field(None, alias="thumbnailUrl")

class Album(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    album_id: str = Field(..., alias="browseId")
    title: str
    artist: str
    year: Optional[str] = None
    thumbnail_url: Optional[str] = Field(None, alias="thumbnailUrl")

class Playlist(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    playlist_id: str = Field(..., alias="playlistId")
    title: str
    count: Optional[int] = None
    thumbnail_url: Optional[str] = Field(None, alias="thumbnailUrl")
