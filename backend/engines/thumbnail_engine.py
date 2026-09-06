import io
import logging
from pathlib import Path
from PIL import Image

from domain.thumbnail import Thumbnail
from domain.youtube_metadata import YoutubeMetadata
from engines.thumbnail_prompt_engine import ThumbnailPromptEngine
from providers.image_generation_provider import ImageGenerationProvider
from providers.media_storage import LocalMediaStorage

logger = logging.getLogger(__name__)


class ThumbnailEngineError(Exception):
    """Raised when thumbnail generation fails."""


class ThumbnailEngine:
    def __init__(
        self,
        *,
        media_storage: LocalMediaStorage,
        image_provider: ImageGenerationProvider,
        prompt_engine: ThumbnailPromptEngine | None = None,
    ):
        self.media_storage = media_storage
        self.image_provider = image_provider
        self.prompt_engine = prompt_engine or ThumbnailPromptEngine()

    def run(
        self,
        *,
        metadata: YoutubeMetadata,
        hook_line: str = "",
        topic: str = "",
        thesis: str = "",
        project_id: str,
        run_id: str,
    ) -> Thumbnail:
        file_name = "thumbnail.png"
        storage_key = f"projects/{project_id}/runs/{run_id}/{file_name}"
        output_path = self.media_storage.ensure_parent(storage_key)

        try:
            # 1. Generate viral thumbnail concept & FLUX prompt
            concept = self.prompt_engine.run(
                topic=topic,
                title=metadata.title,
                hook_text=hook_line,
                thesis=thesis,
                thumbnail_concept=metadata.thumbnail_concept,
            )
            logger.info("Generated thumbnail concept: %s", concept.visual_concept)
            logger.info("Image prompt: %s", concept.image_prompt)

            # 2. Generate raw image bytes via ImageGenerationProvider
            raw_bytes = self.image_provider.generate_image(
                prompt=concept.image_prompt,
                negative_prompt=concept.negative_prompt,
            )

            # 3. Format and crop to exact 1280x720 PNG using Pillow
            img = Image.open(io.BytesIO(raw_bytes))
            target_w, target_h = 1280, 720
            target_ratio = target_w / target_h
            img_ratio = img.width / img.height

            if img_ratio > target_ratio:
                new_h = target_h
                new_w = int(target_h * img_ratio)
            else:
                new_w = target_w
                new_h = int(target_w / img_ratio)

            resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            cropped = resized.crop((left, top, left + target_w, top + target_h))

            # Save PNG to storage
            cropped.save(output_path, format="PNG")
            size_bytes = output_path.stat().st_size

            provider_name = getattr(self.image_provider, "last_provider_used", None) or "ai_image"

            return Thumbnail(
                storage_key=storage_key,
                file_name=file_name,
                content_type="image/png",
                width=1280,
                height=720,
                size_bytes=size_bytes,
                headline=concept.headline,
                image_prompt=concept.image_prompt,
                visual_concept=concept.visual_concept,
                provider_used=provider_name,
            )
        except Exception as exc:
            raise ThumbnailEngineError(f"AI Thumbnail generation failed: {exc}") from exc
