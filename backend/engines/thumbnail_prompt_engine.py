from dataclasses import dataclass
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from providers.llm_provider import (
    LLMJsonRequest,
    LLMMessage,
    LLMProvider,
    LLMProviderError,
)


class ThumbnailPromptConcept(BaseModel):
    headline: str = Field(
        description="The exact 2-4 word text to be rendered on the thumbnail in quotes (e.g. 'SALARY UP / BUT POORER' or '₹1 CRORE TRAP')"
    )
    visual_tension: str = Field(
        default="",
        description="The central visual contradiction, tension, or curiosity gap emerging from the specific story",
    )
    focal_element: str = Field(
        default="",
        description="The dominant visual hero (human subject, financial object, or physical metaphor)",
    )
    visual_concept: str = Field(
        description="2-3 sentence strategic explanation of why this visual triggers clicks and complements the title"
    )
    image_prompt: str = Field(
        description="Complete production-grade text-to-image prompt instructing the AI to render the entire thumbnail with native typography"
    )
    negative_prompt: str = Field(
        default="blurry, low quality, deformed hands, extra fingers, cartoon, watermark, signature, misspelled words, illegible text, distorted letters, cluttered background, bad anatomy, low contrast"
    )


THUMBNAIL_PROMPT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "headline": {
            "type": "string",
            "description": "Short, punchy 2-4 word phrase in uppercase to be rendered natively inside the thumbnail (e.g. 'SALARY UP / BUT POORER', '₹1 CRORE TRAP', '6% VS 12%'). Must NOT repeat the full video title.",
        },
        "visual_tension": {
            "type": "string",
            "description": "The central visual contradiction, tension, or curiosity gap emerging from the specific story that stops the viewer from scrolling.",
        },
        "focal_element": {
            "type": "string",
            "description": "The single dominant visual hero (e.g. human subject with specific emotion, specific financial object, or physical metaphor).",
        },
        "visual_concept": {
            "type": "string",
            "description": "Strategic explanation of the packaging: how the visual tension, focal element, and headline hook the viewer's curiosity without repeating the title.",
        },
        "image_prompt": {
            "type": "string",
            "description": "Production-grade text-to-image prompt for modern AI generators. MUST specify: 16:9 aspect ratio, exact headline text enclosed in quotation marks with size/style/placement instructions, dominant focal subject, visual tension elements, cinematic lighting, and dark high-contrast backdrop.",
        },
        "negative_prompt": {
            "type": "string",
            "description": "Negative prompt. Must NOT include 'text' or 'typography'. Must include: 'blurry, low quality, deformed hands, extra fingers, cartoon, watermark, signature, misspelled words, illegible text, distorted letters, cluttered background, bad anatomy'.",
        },
    },
    "required": [
        "headline",
        "visual_tension",
        "focal_element",
        "visual_concept",
        "image_prompt",
        "negative_prompt",
    ],
}


class ThumbnailPromptEngineError(Exception):
    """Raised when prompt generation fails."""


class ThumbnailPromptEngine:
    def __init__(self, llm_provider: LLMProvider | None = None):
        self.llm_provider = llm_provider
        self.system_prompt_path = (
            Path(__file__).resolve().parents[1]
            / "app"
            / "assets"
            / "prompts"
            / "thumbnail_prompt_system.txt"
        )

    def run(
        self,
        *,
        topic: str,
        title: str,
        hook_text: str = "",
        thesis: str = "",
        thumbnail_concept: str = "",
    ) -> ThumbnailPromptConcept:
        if self.llm_provider is None:
            raise ThumbnailPromptEngineError(
                "LLM provider is required for ThumbnailPromptEngine. Fallback prompts are disabled."
            )

        system_instruction = self.system_prompt_path.read_text(encoding="utf-8")

        user_content = f"""Please design a high-CTR YouTube finance thumbnail concept and complete image generation prompt for this video:

VIDEO TOPIC: {topic}
YOUTUBE TITLE: {title}
SCRIPT THESIS: {thesis}
HOOK SCRIPT: {hook_text}
INITIAL THUMBNAIL HOOK: {thumbnail_concept}

Analyze the financial core of this specific story. Independently invent the single strongest visual concept for THIS exact video without forcing it into any predefined template or category. Identify the central visual tension, select the most powerful 2-4 word headline (which complements rather than repeats the title), determine the dominant focal point, and construct a complete production-grade image prompt where the headline typography is natively rendered as part of the image.
"""


        request = LLMJsonRequest(
            messages=[
                LLMMessage(role="system", content=system_instruction),
                LLMMessage(role="user", content=user_content),
            ],
            schema_name="thumbnail_prompt_concept",
            response_schema=THUMBNAIL_PROMPT_SCHEMA,
            temperature=0.7,
        )

        try:
            response = self.llm_provider.generate_json(request)
            payload = response.payload
            return ThumbnailPromptConcept.model_validate(payload)
        except Exception as exc:
            raise ThumbnailPromptEngineError(f"Failed to generate thumbnail concept: {exc}") from exc
