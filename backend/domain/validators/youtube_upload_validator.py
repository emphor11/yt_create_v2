from domain.validation import ValidationResult
from domain.youtube_upload import YoutubeUpload


class YoutubeUploadValidator:
    def validate(self, upload: YoutubeUpload) -> ValidationResult:
        errors: list[str] = []

        if upload.upload_status == "failed":
            if not upload.error_message:
                errors.append("Failed YouTube upload requires an error_message.")
            return ValidationResult(status="failed", errors=errors)

        if not upload.youtube_video_id or not upload.youtube_video_id.strip():
            errors.append("Successful YouTube upload requires a youtube_video_id.")

        if not upload.youtube_url or not (
            upload.youtube_url.startswith("https://youtu.be/")
            or upload.youtube_url.startswith("https://www.youtube.com/watch")
        ):
            errors.append("youtube_url must start with https://youtu.be/ or https://www.youtube.com/watch")

        if not upload.title or not upload.title.strip():
            errors.append("YouTube upload requires a video title.")

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")
