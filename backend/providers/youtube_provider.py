import os
from pathlib import Path
from typing import Any

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
except ImportError:
    Credentials = None
    Request = None
    build = None
    HttpError = Exception
    MediaFileUpload = None


class YouTubeProviderError(Exception):
    """Raised when a YouTube API operation fails."""


class YouTubeProvider:
    def __init__(self, token_path: str | Path | None = None):
        if token_path is None:
            backend_root = Path(__file__).resolve().parents[1]
            token_path = backend_root / "credentials" / "youtube_token.json"
        self.token_path = Path(token_path)

    def get_credentials(self) -> Any:
        if Credentials is None:
            raise YouTubeProviderError(
                "Google client libraries not installed. Please install google-api-python-client and google-auth-oauthlib."
            )
        if not self.token_path.exists():
            raise YouTubeProviderError(
                f"YouTube OAuth token not found at {self.token_path}. "
                "Please run 'python backend/scripts/authenticate_youtube.py' first to authorize your YouTube channel."
            )

        try:
            creds = Credentials.from_authorized_user_file(
                str(self.token_path),
                scopes=["https://www.googleapis.com/auth/youtube.upload"],
            )
        except Exception as exc:
            raise YouTubeProviderError(f"Failed to load YouTube credentials from {self.token_path}: {exc}") from exc

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self.token_path.write_text(creds.to_json(), encoding="utf-8")
            except Exception as exc:
                raise YouTubeProviderError(f"Failed to refresh YouTube access token: {exc}") from exc

        if not creds or not creds.valid:
            raise YouTubeProviderError("YouTube credentials are invalid. Please run authenticate_youtube.py again.")

        return creds

    def upload_video(
        self,
        *,
        video_path: Path,
        title: str,
        description: str,
        tags: list[str],
        category_id: str = "27",
        privacy_status: str = "private",
    ) -> dict[str, str]:
        if not video_path.exists():
            raise YouTubeProviderError(f"Video file not found at {video_path}")

        creds = self.get_credentials()
        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": tags[:50],
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            chunksize=10 * 1024 * 1024,  # 10MB chunks
            resumable=True,
        )

        try:
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )
            response = None
            while response is None:
                status, response = request.next_chunk()

            video_id = response.get("id")
            if not video_id:
                raise YouTubeProviderError(f"YouTube upload succeeded but no video ID returned: {response}")

            return {
                "video_id": video_id,
                "video_url": f"https://youtu.be/{video_id}",
            }
        except HttpError as exc:
            raise YouTubeProviderError(f"YouTube API HttpError during upload: {exc}") from exc
        except Exception as exc:
            raise YouTubeProviderError(f"YouTube upload failed: {exc}") from exc

    def set_thumbnail(self, *, video_id: str, thumbnail_path: Path) -> bool:
        if not thumbnail_path.exists():
            raise YouTubeProviderError(f"Thumbnail file not found at {thumbnail_path}")

        creds = self.get_credentials()
        youtube = build("youtube", "v3", credentials=creds)

        media = MediaFileUpload(
            str(thumbnail_path),
            mimetype="image/png",
            resumable=False,
        )

        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=media,
            ).execute()
            return True
        except HttpError as exc:
            raise YouTubeProviderError(f"YouTube API error setting thumbnail: {exc}") from exc
        except Exception as exc:
            raise YouTubeProviderError(f"Failed to set YouTube thumbnail: {exc}") from exc
