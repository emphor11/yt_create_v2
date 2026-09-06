from pathlib import PurePosixPath

from domain.thumbnail import Thumbnail
from domain.validation import ValidationResult


class ThumbnailValidator:
    def validate(self, thumbnail: Thumbnail) -> ValidationResult:
        errors: list[str] = []

        if not thumbnail.storage_key or not thumbnail.storage_key.strip():
            errors.append("Thumbnail requires a valid storage_key.")
        else:
            path = PurePosixPath(thumbnail.storage_key)
            if path.is_absolute():
                errors.append("Thumbnail storage_key must be relative.")
            if ".." in path.parts:
                errors.append("Thumbnail storage_key must not contain parent directory segments.")
            if not thumbnail.storage_key.endswith(".png"):
                errors.append("Thumbnail storage_key must point to a .png file.")

        if thumbnail.content_type != "image/png":
            errors.append("Thumbnail content_type must be image/png.")

        if thumbnail.width != 1280 or thumbnail.height != 720:
            errors.append(f"Thumbnail dimensions must be 1280x720 (got {thumbnail.width}x{thumbnail.height}).")

        if thumbnail.size_bytes <= 0:
            errors.append("Thumbnail size_bytes must be greater than 0.")

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")
