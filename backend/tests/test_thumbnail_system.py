"""
Unit and integration tests for the specialized Finance YouTube Thumbnail system.
Tests:
- ThumbnailPromptConcept schema validation & backward compatibility
- ThumbnailPromptEngine fallback & prompt construction
- ThumbnailEngine 1280x720 format, cropping, and domain model mapping
- ThumbnailValidator constraints
- ImageGenerationProvider composite fallback behavior
"""
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock
from PIL import Image
import pytest

from domain.thumbnail import Thumbnail
from domain.youtube_metadata import YoutubeMetadata
from domain.validators.thumbnail_validator import ThumbnailValidator
from engines.thumbnail_prompt_engine import (
    ThumbnailPromptConcept,
    ThumbnailPromptEngine,
    THUMBNAIL_PROMPT_SCHEMA,
)
from engines.thumbnail_engine import ThumbnailEngine
from providers.llm_provider import LLMJsonRequest, LLMJsonResponse, LLMProviderMetadata
from providers.media_storage import LocalMediaStorage


def test_thumbnail_prompt_concept_schema_backward_compatibility():
    """Verify that existing minimal arguments (headline, visual_concept, image_prompt, negative_prompt) still work."""
    concept = ThumbnailPromptConcept(
        headline="SALARY UP",
        visual_concept="Juxtaposition of salary vs inflation.",
        image_prompt="A 16:9 thumbnail showing a shocked professional.",
        negative_prompt="blurry, low quality",
    )
    assert concept.headline == "SALARY UP"
    assert concept.visual_concept == "Juxtaposition of salary vs inflation."
    assert "SALARY UP" in concept.headline


def test_thumbnail_prompt_concept_full_fields():
    """Verify all strategic story-driven fields serialize and validate cleanly."""
    concept = ThumbnailPromptConcept(
        headline="₹1 CRORE TRAP",
        visual_tension="Massive ₹1 Crore nest egg decaying into insufficient retirement cash.",
        focal_element="Monumental glowing ₹1 Crore vault with a leaking fracture.",
        visual_concept="Creates curiosity around the standard retirement milestone.",
        image_prompt="YouTube finance thumbnail, 16:9 aspect ratio. Bold 3D white text '₹1 CRORE TRAP'...",
        negative_prompt="blurry, distorted letters",
    )
    dump = concept.model_dump()
    assert dump["headline"] == "₹1 CRORE TRAP"
    assert dump["visual_tension"] == "Massive ₹1 Crore nest egg decaying into insufficient retirement cash."
    assert dump["focal_element"] == "Monumental glowing ₹1 Crore vault with a leaking fracture."


def test_thumbnail_prompt_engine_fails_loudly_when_no_llm():
    """When LLM provider is None, ThumbnailPromptEngine fails loudly instead of falling back to a hardcoded prompt."""
    from engines.thumbnail_prompt_engine import ThumbnailPromptEngineError

    engine = ThumbnailPromptEngine(llm_provider=None)
    with pytest.raises(ThumbnailPromptEngineError, match="LLM provider is required"):
        engine.run(
            topic="Retirement Math",
            title="Why ₹1 Crore Isn't Enough to Retire",
            hook_text="You think one crore makes you safe.",
            thesis="Inflation destroys fixed wealth.",
            thumbnail_concept="₹1 CRORE TRAP",
        )


def test_huggingface_image_provider_passes_16_9_dimensions(monkeypatch):
    """HuggingFaceImageProvider must request native 16:9 widescreen dimensions (width=1280, height=720) and negative prompt."""
    from providers.image_generation_provider import HuggingFaceImageProvider

    mock_client = MagicMock()
    mock_img = Image.new("RGB", (1280, 720), color=(10, 10, 10))
    mock_client.text_to_image.return_value = mock_img

    mock_inference_class = MagicMock(return_value=mock_client)
    monkeypatch.setattr("huggingface_hub.InferenceClient", mock_inference_class)

    provider = HuggingFaceImageProvider(token="mock_token", models=["black-forest-labs/FLUX.1-schnell"])
    raw_bytes = provider.generate_image("A finance thumbnail", negative_prompt="blurry, distorted")

    assert len(raw_bytes) > 0
    assert mock_client.text_to_image.call_count == 1
    call_kwargs = mock_client.text_to_image.call_args[1]
    assert call_kwargs["width"] == 1280
    assert call_kwargs["height"] == 720
    assert call_kwargs["negative_prompt"] == "blurry, distorted"
    assert call_kwargs["model"] == "black-forest-labs/FLUX.1-schnell"


def test_thumbnail_prompt_engine_with_llm():
    """When LLM provider is present, prompt is sent with finance instructions and structured output is validated."""
    mock_llm = MagicMock()
    mock_llm.generate_json.return_value = LLMJsonResponse(
        payload={
            "headline": "SALARY UP / BUT POORER",
            "visual_tension": "Nominal salary rising while real purchasing power collapses.",
            "focal_element": "Shocked Indian professional beside glowing downward currency spiral.",
            "visual_concept": "Hooks viewers who received a raise but feel poorer.",
            "image_prompt": "YouTube finance thumbnail, 16:9. Huge bold 3D text 'SALARY UP' in green...",
            "negative_prompt": "blurry, misspelled text, distorted letters",
        },
        metadata=LLMProviderMetadata(provider="mock", model="mock-llm"),
    )

    engine = ThumbnailPromptEngine(llm_provider=mock_llm)
    concept = engine.run(
        topic="Inflation and Salaries",
        title="Your Salary Is Going Up, But You're Still Getting Poorer",
        hook_text="Got a 10% raise this year? You might actually be 5% poorer.",
        thesis="Lifestyle inflation and real inflation consume income gains.",
        thumbnail_concept="SALARY UP",
    )

    assert concept.headline == "SALARY UP / BUT POORER"
    assert mock_llm.generate_json.call_count == 1
    call_args = mock_llm.generate_json.call_args[0][0]
    assert "Your Salary Is Going Up, But You're Still Getting Poorer" in call_args.messages[1].content
    assert call_args.response_schema == THUMBNAIL_PROMPT_SCHEMA


def test_thumbnail_engine_creates_1280x720_png(tmp_path: Path):
    """ThumbnailEngine resizes raw image bytes to exactly 1280x720 PNG without template/story_type restrictions."""
    storage = LocalMediaStorage(tmp_path)

    # Fake raw image of arbitrary size (e.g. 1024x1024)
    buf = BytesIO()
    Image.new("RGB", (1024, 1024), color=(8, 14, 26)).save(buf, format="PNG")
    raw_bytes = buf.getvalue()

    mock_image_provider = MagicMock()
    mock_image_provider.generate_image.return_value = raw_bytes
    mock_image_provider.last_provider_used = "pollinations_flux"

    mock_prompt_engine = MagicMock()
    mock_prompt_engine.run.return_value = ThumbnailPromptConcept(
        headline="SALARY UP / POORER",
        visual_tension="Salary rising vs purchasing power drop",
        focal_element="Indian professional looking shocked",
        visual_concept="Strong juxtaposition",
        image_prompt="A YouTube thumbnail...",
        negative_prompt="blurry",
    )

    engine = ThumbnailEngine(
        media_storage=storage,
        image_provider=mock_image_provider,
        prompt_engine=mock_prompt_engine,
    )

    metadata = YoutubeMetadata(
        title="Salary vs Inflation",
        description="Video description",
        tags=["finance"],
        category_id="27",
        thumbnail_concept="SALARY UP",
    )

    thumb = engine.run(
        metadata=metadata,
        hook_line="Got a raise?",
        topic="Salary",
        thesis="Inflation eats salary",
        project_id="proj_1",
        run_id="run_1",
    )

    assert thumb.width == 1280
    assert thumb.height == 720
    assert thumb.headline == "SALARY UP / POORER"
    assert thumb.provider_used == "pollinations_flux"

    # Verify physical file on disk is valid 1280x720 PNG
    saved_img = Image.open(storage.path_for_key(thumb.storage_key))
    assert saved_img.size == (1280, 720)
    assert saved_img.format == "PNG"

    # Verify ThumbnailValidator passes
    validator = ThumbnailValidator()
    validation = validator.validate(thumb)
    assert validation.status == "valid"
