from enum import Enum


class PipelineStage(str, Enum):
    TOPIC_REQUEST = "topic_request"
    RESEARCH = "research"
    NARRATIVE_PLAN = "narrative_plan"
    HOOK = "hook"
    SCRIPT_VISUAL_STRATEGY = "script_visual_strategy"
    QUALITY_REVIEW = "quality_review"
    VOICE_GENERATION = "voice_generation"
    SCRIPT_BRIEF = "script_brief"
    NARRATIVE_ARC = "narrative_arc"
    SCRIPT_DRAFT = "script_draft"
    SCENE_SCRIPT = "scene_script"
    SEMANTIC_SCENE = "semantic_scene"
    VISUAL_EVENT_SEQUENCE = "visual_event_sequence"
    VISUAL_PLAN = "visual_plan"
    TIMING = "timing"
    RENDER_SPEC = "render_spec"
    RENDER = "render"
