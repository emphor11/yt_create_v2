from typing import Literal
from pydantic import BaseModel, ConfigDict


UploadStatus = Literal["succeeded", "failed"]


class YoutubeUpload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    youtube_video_id: str
    youtube_url: str
    target_account: Literal["test", "production"] = "test"
    channel_title: str | None = None
    upload_status: UploadStatus = "succeeded"
    thumbnail_attached: bool = False
    title: str
    privacy_status: str = "private"
    error_message: str | None = None
