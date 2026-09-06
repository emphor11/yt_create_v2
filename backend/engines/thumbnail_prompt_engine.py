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
    headline: str = Field(description="A short, punchy 2-4 word phrase representing the psychological hook")
    visual_concept: str = Field(description="2-3 sentence strategic explanation of why this visual triggers clicks")
    image_prompt: str = Field(description="Detailed text-to-image prompt following the universal formula")
    negative_prompt: str = Field(default="blurry, low quality, deformed hands, extra fingers, cartoon, 3d render, watermark, text, logos, cluttered, bad anatomy")


THUMBNAIL_PROMPT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "headline": {
            "type": "string",
            "description": "A short, punchy 2-4 word phrase representing the psychological hook",
        },
        "visual_concept": {
            "type": "string",
            "description": "2-3 sentence strategic explanation of why this visual triggers clicks",
        },
        "image_prompt": {
            "type": "string",
            "description": "Detailed text-to-image prompt following the universal formula",
        },
        "negative_prompt": {
            "type": "string",
            "description": "Artifacts and attributes to avoid in generation",
        },
    },
    "required": ["headline", "visual_concept", "image_prompt", "negative_prompt"],
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
            # Fallback heuristic if LLM is unavailable
            headline = thumbnail_concept or "THE TRAP"
            visual_concept = f"Dramatic visual showing the high-stakes dilemma behind {topic}."
            image_prompt = (
                f"Cinematic 16:9 photography, 8k resolution, shot on 35mm lens, dramatic lighting, "
                f"intense emotion, subject dealing with {topic}, high contrast, dark moody background, "
                f"vibrant amber rim lighting, rule of thirds, clean negative space."
            )
            return ThumbnailPromptConcept(
                headline=headline,
                visual_concept=visual_concept,
                image_prompt=image_prompt,
            )

        system_instruction = self.system_prompt_path.read_text(encoding="utf-8")

        user_content = f"""Please design a viral YouTube thumbnail concept and FLUX.1 image prompt for this video:

VIDEO TOPIC: {topic}
YOUTUBE TITLE: {title}
SCRIPT THESIS: {thesis}
HOOK CONCEPT / SCRIPT: {hook_text}
PRELIMINARY THUMBNAIL HOOK: {thumbnail_concept}

Design the ultimate high-CTR visual concept, punchy headline, and detailed image prompt adhering to the 3-second rule and high emotional contrast.
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
