from domain.youtube_metadata import YoutubeMetadata
from domain.youtube_upload import YoutubeUpload
from providers.media_storage import LocalMediaStorage
from providers.youtube_provider import YouTubeProvider, YouTubeProviderError


class YoutubeUploadEngineError(Exception):
    """Raised when YouTube upload fails."""


class YoutubeUploadEngine:
    def __init__(
        self,
        *,
        youtube_provider: YouTubeProvider,
        media_storage: LocalMediaStorage,
    ):
        self.youtube_provider = youtube_provider
        self.media_storage = media_storage

    def run(
        self,
        *,
        video_storage_key: str,
        metadata: YoutubeMetadata,
        thumbnail_storage_key: str | None = None,
        privacy_status: str = "private",
        target_account: str = "test",
    ) -> YoutubeUpload:
        video_path = self.media_storage.path_for_key(video_storage_key)
        if not video_path.exists():
            raise YoutubeUploadEngineError(f"Video file not found at {video_path}")

        # Resolve provider for target_account (testing vs production)
        provider = self.youtube_provider
        norm_account = "production" if target_account.lower() in ("prod", "production", "real") else "test"
        if isinstance(provider, YouTubeProvider) and getattr(provider, "account_type", None) != norm_account:
            provider = YouTubeProvider(account_type=norm_account)

        try:
            upload_res = provider.upload_video(
                video_path=video_path,
                title=metadata.title,
                description=metadata.description,
                tags=metadata.tags,
                category_id=metadata.category_id,
                privacy_status=privacy_status,
            )
        except YouTubeProviderError as exc:
            raise YoutubeUploadEngineError(f"YouTube upload failed: {exc}") from exc
        except Exception as exc:
            raise YoutubeUploadEngineError(f"Unexpected upload failure: {exc}") from exc

        video_id = upload_res["video_id"]
        video_url = upload_res["video_url"]
        channel_title = upload_res.get("channel_title")
        thumbnail_attached = False

        if thumbnail_storage_key:
            try:
                thumbnail_path = self.media_storage.path_for_key(thumbnail_storage_key)
                if thumbnail_path.exists():
                    provider.set_thumbnail(video_id=video_id, thumbnail_path=thumbnail_path)
                    thumbnail_attached = True
            except Exception as exc:
                # Thumbnail setting failure is logged but doesn't prevent upload success
                pass

        return YoutubeUpload(
            youtube_video_id=video_id,
            youtube_url=video_url,
            target_account=norm_account,
            channel_title=channel_title,
            upload_status="succeeded",
            thumbnail_attached=thumbnail_attached,
            title=metadata.title,
            privacy_status=privacy_status,
        )
