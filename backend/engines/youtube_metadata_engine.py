from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from domain.hook import Hook
from domain.render_spec import RenderSpec
from domain.research_packet import ResearchPacket
from domain.youtube_metadata import YoutubeMetadata
from providers.llm_provider import (
    LLMJsonRequest,
    LLMMessage,
    LLMProvider,
    LLMProviderError,
    LLMProviderMetadata,
)


YOUTUBE_METADATA_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Engaging, high-CTR YouTube video title under 95 characters. Avoid clickbait that misleads.",
        },
        "description": {
            "type": "string",
            "description": "Full YouTube video description with chapter timestamps (starting with 00:00 Intro), summary, key takeaways, and hashtags.",
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "10-15 relevant search tags for the video.",
        },
        "category_id": {
            "type": "string",
            "description": "YouTube Category ID (e.g. '27' for Education, '28' for Science & Technology).",
        },
        "thumbnail_concept": {
            "type": "string",
            "description": "A short, punchy 2-5 word phrase to display prominently on the thumbnail (e.g. 'THE HIDDEN COST', 'WHY IT MATTERS').",
        },
    },
    "required": [
        "title",
        "description",
        "tags",
        "category_id",
        "thumbnail_concept",
    ],
}


@dataclass(frozen=True)
class YoutubeMetadataResult:
    metadata: YoutubeMetadata
    provider_metadata: LLMProviderMetadata | None = None
    raw_payload: dict[str, Any] | None = None


class YoutubeMetadataEngineError(Exception):
    def __init__(
        self,
        message: str,
        *,
        raw_payload: dict[str, Any] | None = None,
        provider_metadata: LLMProviderMetadata | None = None,
    ):
        super().__init__(message)
        self.raw_payload = raw_payload or {}
        self.provider_metadata = provider_metadata


class YoutubeMetadataEngine:
    def __init__(self, llm_provider: LLMProvider | None = None):
        self.llm_provider = llm_provider

    def run(
        self,
        *,
        render_spec: RenderSpec,
        hook: Hook | None = None,
        research: ResearchPacket | None = None,
        topic: str = "",
        angle: str = "",
    ) -> YoutubeMetadataResult:
        if self.llm_provider is None:
            raise YoutubeMetadataEngineError("LLMProvider is required for YoutubeMetadataEngine.")

        # Extract timestamps and scene narration to provide precise chapter markers
        fps = render_spec.fps or 30
        if isinstance(render_spec.props, dict):
            raw_scenes = render_spec.props.get("scenes", [])
        else:
            raw_scenes = getattr(render_spec.props, "scenes", [])

        chapter_cues: list[str] = []
        if raw_scenes:
            for idx, scene in enumerate(raw_scenes):
                if hasattr(scene, "model_dump"):
                    scene_dict = scene.model_dump()
                elif isinstance(scene, dict):
                    scene_dict = scene
                else:
                    scene_dict = {}

                start_f = scene_dict.get("start_frame", 0)
                seconds = int(start_f / fps)
                mm = seconds // 60
                ss = seconds % 60
                ts = f"{mm:02d}:{ss:02d}"
                narr = (scene_dict.get("narration_text") or scene_dict.get("scene_id") or f"Section {idx + 1}").strip()
                chapter_cues.append(f"{ts} - {narr[:80]}")
        else:
            chapter_cues = ["00:00 - Introduction", "00:30 - Deep Dive", "01:00 - Conclusion"]


        hook_text = hook.conceptual_hook if hook else ""
        hook_script = hook.script_text if hook else ""
        facts_summary = "\n".join(f"- {fact}" for fact in (research.verified_facts[:5] if research else []))

        prompt_content = (
            f"Topic: {topic or (research.topic if research else 'Video')}\n"
            f"Angle: {angle}\n"
            f"Hook Concept: {hook_text}\n"
            f"Opening Script: {hook_script}\n"
            f"Key Facts:\n{facts_summary}\n\n"
            f"Video Scene Timeline Markers:\n" + "\n".join(chapter_cues) + "\n\n"
            "Requirements:\n"
            "1. Title: Create a high-CTR, punchy YouTube title (strictly ≤ 95 characters).\n"
            "2. Description: Write an informative, engaging description. MUST include YouTube Chapters starting at '00:00 Intro', followed by chapter timestamps matching the video scene breakdown. End with 3-5 relevant hashtags.\n"
            "3. Tags: Provide 10-15 targeted SEO search tags.\n"
            "4. Category: Set category_id (e.g. '27' for Education).\n"
            "5. Thumbnail Concept: Provide a 2-5 word bold phrase suitable for a visual thumbnail header."
        )

        llm_request = LLMJsonRequest(
            schema_name="YoutubeMetadata",
            response_schema=YOUTUBE_METADATA_RESPONSE_SCHEMA,
            messages=[
                LLMMessage(
                    role="system",
                    content=(
                        "You are an expert YouTube SEO strategist, copywriter, and metadata producer. "
                        "Your job is to generate high-performing, authentic YouTube metadata including title, "
                        "structured description with chapter timestamps, tags, and category ID."
                    ),
                ),
                LLMMessage(
                    role="user",
                    content=prompt_content,
                ),
            ],
            temperature=0.4,
            max_tokens=2048,
        )

        try:
            response = self.llm_provider.generate_json(llm_request)
        except LLMProviderError as error:
            raise YoutubeMetadataEngineError(f"LLM metadata generation failed: {error}") from error

        payload = dict(response.payload)
        # Ensure title does not exceed 100 characters
        if "title" in payload and isinstance(payload["title"], str):
            payload["title"] = payload["title"].strip()[:100]

        try:
            metadata = YoutubeMetadata.model_validate(payload)
        except ValidationError as error:
            raise YoutubeMetadataEngineError(
                f"LLM returned invalid YouTube metadata: {error}",
                raw_payload=payload,
                provider_metadata=response.metadata,
            ) from error

        return YoutubeMetadataResult(
            metadata=metadata,
            provider_metadata=response.metadata,
            raw_payload=payload,
        )
