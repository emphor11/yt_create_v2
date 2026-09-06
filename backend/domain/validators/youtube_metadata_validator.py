import re
from domain.validation import ValidationResult
from domain.youtube_metadata import YoutubeMetadata


class YoutubeMetadataValidator:
    def validate(self, metadata: YoutubeMetadata) -> ValidationResult:
        errors: list[str] = []

        if not metadata.title or not metadata.title.strip():
            errors.append("YouTube title is required and cannot be empty.")
        elif len(metadata.title) > 100:
            errors.append(f"YouTube title cannot exceed 100 characters (got {len(metadata.title)}).")

        if not metadata.description or not metadata.description.strip():
            errors.append("YouTube description is required and cannot be empty.")
        elif len(metadata.description) > 5000:
            errors.append(f"YouTube description cannot exceed 5000 characters (got {len(metadata.description)}).")

        # YouTube chapters require 00:00 timestamp
        if not re.search(r"\b00:00\b", metadata.description):
            errors.append("YouTube description should include timestamps starting at 00:00.")

        if not metadata.tags or len(metadata.tags) < 3:
            errors.append("YouTube metadata requires at least 3 tags.")
        elif len(metadata.tags) > 50:
            errors.append("YouTube metadata cannot exceed 50 tags.")

        if not metadata.category_id or not metadata.category_id.strip():
            errors.append("YouTube category_id is required.")

        if not metadata.thumbnail_concept or not metadata.thumbnail_concept.strip():
            errors.append("Thumbnail concept is required.")

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")
