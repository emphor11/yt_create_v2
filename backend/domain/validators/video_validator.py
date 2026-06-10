from pathlib import PurePosixPath

from domain.render_spec import RenderSpec
from domain.validation import ValidationResult
from domain.video import Video


class VideoValidator:
    def validate(self, video: Video, *, render_spec: RenderSpec) -> ValidationResult:
        errors: list[str] = []

        if video.scene_id != render_spec.scene_id:
            errors.append("Video scene_id must match RenderSpec scene_id.")
        if video.fps != render_spec.fps:
            errors.append("Video fps must match RenderSpec fps.")
        if video.duration_frames != render_spec.duration_frames:
            errors.append("Video duration_frames must match RenderSpec duration_frames.")
        if video.file_name != f"{render_spec.scene_id}.mp4":
            errors.append("Video file_name must match the scene id and .mp4 extension.")
        if video.content_type != "video/mp4":
            errors.append("Video content_type must be video/mp4.")

        if video.render_status == "succeeded":
            self._validate_success(video, errors)
        elif video.render_status == "failed":
            self._validate_failure(video, errors)

        if video.render_status == "failed":
            return ValidationResult(status="failed", errors=errors)
        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")

    @staticmethod
    def _validate_success(video: Video, errors: list[str]) -> None:
        if not video.storage_key:
            errors.append("Successful Video requires a storage_key.")
        else:
            VideoValidator._validate_storage_key(video.storage_key, errors)
        if video.size_bytes is None or video.size_bytes <= 0:
            errors.append("Successful Video requires a positive size_bytes value.")
        if video.error_message:
            errors.append("Successful Video must not include an error_message.")

    @staticmethod
    def _validate_failure(video: Video, errors: list[str]) -> None:
        if video.storage_key:
            errors.append("Failed Video must not include a storage_key.")
        if video.size_bytes is not None:
            errors.append("Failed Video must not include size_bytes.")
        if not video.error_message:
            errors.append("Failed Video requires an error_message.")

    @staticmethod
    def _validate_storage_key(storage_key: str, errors: list[str]) -> None:
        path = PurePosixPath(storage_key)
        parts = path.parts
        if path.is_absolute():
            errors.append("Video storage_key must be relative.")
        if ".." in parts:
            errors.append("Video storage_key must not contain parent directory segments.")
        if len(parts) != 5:
            errors.append(
                "Video storage_key must use projects/{project_id}/runs/{run_id}/{file_name}."
            )
            return
        if parts[0] != "projects" or parts[2] != "runs":
            errors.append(
                "Video storage_key must use projects/{project_id}/runs/{run_id}/{file_name}."
            )
        if not parts[-1].endswith(".mp4"):
            errors.append("Video storage_key must point to an .mp4 file.")
