"""
Tests for Hook Unified Composition Integration:
Verifies that the Hook participates in the modern Composition Architecture
using HookCompositionPlan, VisualIntent, CompositionPlanner, and CompositionResolver.
"""
import pytest
from unittest.mock import MagicMock

from domain.hook import Hook, VisualDirective
from domain.composition_plan import (
    CompositionBeat,
    FullCompositionPlan,
    HookCompositionPlan,
    IdeaCompositionPlan,
)
from domain.visual_intent import VisualIntent, VisualIntentSequence, ComparisonStructure
from domain.voice_track import VoiceTrack, WordTimestamp
from domain.script_visual_strategy import ScriptVisualStrategy, VideoIdea
from engines.video_assembly.timeline_builder import TimelineBuilder
from engines.composition_assembly_engine import CompositionAssemblyEngine
from engines.visual_intent_engine import VisualIntentEngine
from engines.composition_planner_engine import CompositionPlannerEngine
from providers.llm_provider import LLMJsonRequest, LLMJsonResponse, LLMProviderMetadata


class MockLLMProvider:
    def __init__(self, payload: dict):
        self.payload = payload
        self.last_request: LLMJsonRequest | None = None

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        self.last_request = request
        return LLMJsonResponse(
            payload=self.payload,
            metadata=LLMProviderMetadata(
                provider="mock",
                model="mock-model",
            ),
        )


def test_hook_composition_plan_data_model() -> None:
    """Verifies HookCompositionPlan can be serialized and deserialized inside FullCompositionPlan."""
    hook_plan = HookCompositionPlan(
        hook_id="hook",
        narration="Imagine losing forty percent of your wealth.",
        beats=[
            CompositionBeat(
                beat_id="beat_hook_01",
                composition_id="metric_hero",
                variant="hero",
                composition_data={"value": "40%", "label": "Wealth Loss"},
                trigger_word=None,
                visual_goal="Show 40% loss callout",
            ),
            CompositionBeat(
                beat_id="beat_hook_02",
                composition_id="time_decay",
                composition_data={"fixed_amount": "₹50 lakh", "drop_rate": "40%"},
                trigger_word="wealth",
                visual_goal="Show erosion over time",
            ),
        ],
    )

    full_plan = FullCompositionPlan(
        thesis="Wealth erosion occurs silently.",
        visual_mode="composition",
        hook_plan=hook_plan,
        ideas=[
            IdeaCompositionPlan(
                idea_id="idea_01",
                narration="Here is how inflation strikes.",
                beats=[
                    CompositionBeat(
                        beat_id="beat_01_01",
                        composition_id="broll_caption",
                        composition_data={"caption": "Silent Drag"},
                        trigger_word=None,
                    )
                ],
            )
        ],
    )

    dumped = full_plan.model_dump()
    assert "hook_plan" in dumped
    assert dumped["hook_plan"]["hook_id"] == "hook"
    assert len(dumped["hook_plan"]["beats"]) == 2
    assert dumped["hook_plan"]["beats"][0]["composition_id"] == "metric_hero"

    restored = FullCompositionPlan.model_validate(dumped)
    assert restored.hook_plan is not None
    assert restored.hook_plan.beats[0].composition_id == "metric_hero"
    assert restored.hook_plan.beats[1].trigger_word == "wealth"


def test_visual_intent_engine_hook_mode() -> None:
    """Verifies that VisualIntentEngine accepts is_hook=True and generates valid hook intents."""
    mock_payload = {
        "idea_id": "hook",
        "intents": [
            {
                "intent_id": "intent_01",
                "narration_excerpt": "What if rent is actually building wealth?",
                "what_viewer_must_understand": "Renting can outperform buying when capital is invested",
                "key_values": ["Rent vs Buy"],
                "relationship_type": "comparison",
                "trigger_word": None,
                "comparison": {
                    "subject_a": "Home EMI",
                    "value_a": "₹65K/mo",
                    "subject_b": "Rent & SIP",
                    "value_b": "₹40K SIP",
                    "comparison_dimension": "20-YEAR OUTCOME",
                },
            },
            {
                "intent_id": "intent_02",
                "narration_excerpt": "Over twenty years, the difference compounds into crores.",
                "what_viewer_must_understand": "Long-term compounding creates a massive wealth delta",
                "key_values": ["₹2.4 Crore"],
                "relationship_type": "metric",
                "trigger_word": "twenty",
            },
        ],
    }
    provider = MockLLMProvider(mock_payload)
    engine = VisualIntentEngine(provider)

    result = engine.run(
        idea_id="hook",
        narration="What if rent is actually building wealth? Over twenty years, the difference compounds into crores.",
        topic="Rent vs Buy",
        audience="retail investors",
        is_hook=True,
    )

    assert result.sequence.idea_id == "hook"
    assert len(result.sequence.intents) == 2
    assert result.sequence.intents[0].trigger_word is None
    assert result.sequence.intents[1].trigger_word == "twenty"
    assert "HOOK-SPECIFIC CONSTRAINTS" in provider.last_request.messages[1].content


def test_timeline_builder_with_hook_composition_plan() -> None:
    """Verifies TimelineBuilder uses composition_plan.hook_plan.beats instead of legacy directives."""
    hook = Hook(
        conceptual_hook="Concept",
        script_text="Imagine losing your portfolio. Over ten years, inflation destroys cash.",
        visual_directives=[
            VisualDirective(beat_id="legacy_h1", visual_instruction="Legacy", trigger_word=None)
        ],
    )
    strategy = ScriptVisualStrategy(
        schema_version="1",
        thesis="Inflation destroys cash.",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Idea 1",
                focus_concept="Drag",
                core_teaching_point="Drag point",
                narration="Keep investing regularly.",
            )
        ],
    )
    comp_plan = FullCompositionPlan(
        thesis="Inflation destroys cash.",
        visual_mode="composition",
        hook_plan=HookCompositionPlan(
            hook_id="hook",
            narration=hook.script_text,
            beats=[
                CompositionBeat(
                    beat_id="beat_hook_01",
                    composition_id="metric_hero",
                    trigger_word=None,
                ),
                CompositionBeat(
                    beat_id="beat_hook_02",
                    composition_id="time_decay",
                    trigger_word="inflation",
                ),
            ],
        ),
        ideas=[
            IdeaCompositionPlan(
                idea_id="idea_01",
                narration="Keep investing regularly.",
                beats=[
                    CompositionBeat(
                        beat_id="beat_01_01",
                        composition_id="broll_caption",
                        trigger_word=None,
                    )
                ],
            )
        ],
    )

    voice_track = VoiceTrack(
        voice_id="Joanna",
        audio_file_name="audio.mp3",
        storage_key="audio.mp3",
        duration_seconds=6.0,
        full_script_text="Imagine losing your portfolio. Over ten years, inflation destroys cash. Keep investing regularly.",
        word_timestamps=[
            WordTimestamp(word="Imagine", start_ms=0, end_ms=500),
            WordTimestamp(word="losing", start_ms=510, end_ms=900),
            WordTimestamp(word="your", start_ms=910, end_ms=1100),
            WordTimestamp(word="portfolio", start_ms=1110, end_ms=1600),
            WordTimestamp(word="Over", start_ms=1610, end_ms=1900),
            WordTimestamp(word="ten", start_ms=1910, end_ms=2200),
            WordTimestamp(word="years", start_ms=2210, end_ms=2500),
            WordTimestamp(word="inflation", start_ms=2510, end_ms=2900),
            WordTimestamp(word="destroys", start_ms=2910, end_ms=3300),
            WordTimestamp(word="cash", start_ms=3310, end_ms=3700),
            # Body idea
            WordTimestamp(word="Keep", start_ms=3800, end_ms=4200),
            WordTimestamp(word="investing", start_ms=4210, end_ms=4800),
            WordTimestamp(word="regularly", start_ms=4810, end_ms=5800),
        ],
    )

    builder = TimelineBuilder(fps=30)
    intervals = builder.build_timeline(
        hook=hook,
        strategy=strategy,
        voice_track=voice_track,
        composition_plan=comp_plan,
    )

    # 2 hook composition beats + 1 body composition beat = 3 intervals
    assert len(intervals) == 3
    assert intervals[0].section_type == "hook"
    assert intervals[0].beat_id == "beat_hook_01"
    assert intervals[0].start_frame == 0

    assert intervals[1].section_type == "hook"
    assert intervals[1].beat_id == "beat_hook_02"
    # inflation starts at 2510ms -> frame ~75
    assert intervals[1].start_frame >= 70

    assert intervals[2].section_type == "body"
    assert intervals[2].beat_id == "beat_01_01"


def test_composition_assembly_engine_hook_resolves_via_composition_resolver() -> None:
    """Verifies that CompositionAssemblyEngine resolves hook beats using CompositionResolver."""
    hook = Hook(
        conceptual_hook="Concept",
        script_text="Imagine losing 40% of wealth. Over ten years, inflation destroys cash.",
        visual_directives=[
            VisualDirective(
                beat_id="legacy_h1",
                preferred_component="Typography",
                component_data={"text": "Legacy Typography"},
                trigger_word=None,
            )
        ],
    )
    strategy = ScriptVisualStrategy(
        schema_version="1",
        thesis="Inflation destroys cash.",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Idea 1",
                focus_concept="Drag",
                core_teaching_point="Drag point",
                narration="Keep investing regularly.",
            )
        ],
    )
    comp_plan = FullCompositionPlan(
        thesis="Inflation destroys cash.",
        visual_mode="composition",
        hook_plan=HookCompositionPlan(
            hook_id="hook",
            narration=hook.script_text,
            beats=[
                CompositionBeat(
                    beat_id="beat_hook_01",
                    composition_id="metric_hero",
                    variant="single_large_callout",
                    composition_data={
                        "value": "40%",
                        "label": "Wealth Erosion Risk",
                        "context": "Inflation Threat",
                    },
                    trigger_word=None,
                    visual_goal="Show 40% erosion metric",
                ),
            ],
        ),
        ideas=[
            IdeaCompositionPlan(
                idea_id="idea_01",
                narration="Keep investing regularly.",
                beats=[
                    CompositionBeat(
                        beat_id="beat_01_01",
                        composition_id="broll_caption",
                        variant="statement",
                        composition_data={"caption": "Keep investing regularly."},
                        trigger_word=None,
                    )
                ],
            )
        ],
    )

    voice_track = VoiceTrack(
        voice_id="Joanna",
        audio_file_name="audio.mp3",
        storage_key="audio.mp3",
        duration_seconds=5.0,
        full_script_text="Imagine losing 40% of wealth. Keep investing regularly.",
        word_timestamps=[
            WordTimestamp(word="Imagine", start_ms=0, end_ms=1000),
            WordTimestamp(word="losing", start_ms=1010, end_ms=2500),
            WordTimestamp(word="Keep", start_ms=2600, end_ms=3500),
            WordTimestamp(word="regularly", start_ms=3510, end_ms=4800),
        ],
    )

    engine = CompositionAssemblyEngine(fps=30)
    render_spec = engine.run(
        scene_id="test_scene",
        hook=hook,
        strategy=strategy,
        composition_plan=comp_plan,
        voice_track=voice_track,
    )

    scenes = render_spec.props.scenes
    assert len(scenes) == 2

    # Hook scene: MUST be resolved to MetricHero via CompositionResolver, NOT Typography
    hook_scene = scenes[0]
    assert hook_scene.component.component_id == "MetricHero"
    assert hook_scene.component.props["value"] == "40%"
    assert hook_scene.component.props["label"] == "Wealth Erosion Risk"

    # Body scene: BrollCaption
    body_scene = scenes[1]
    assert body_scene.component.component_id == "BrollCaption"


def test_composition_assembly_engine_hook_fallback_when_hook_plan_is_none() -> None:
    """Verifies backward compatibility: if hook_plan is None, falls back to legacy directives."""
    hook = Hook(
        conceptual_hook="Concept",
        script_text="Imagine losing 40% of wealth. Keep investing regularly.",
        visual_directives=[
            VisualDirective(
                beat_id="legacy_h1",
                preferred_component="Typography",
                component_data={"text": "Legacy Fallback Text"},
                trigger_word=None,
            )
        ],
    )
    strategy = ScriptVisualStrategy(
        schema_version="1",
        thesis="Inflation destroys cash.",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Idea 1",
                focus_concept="Drag",
                core_teaching_point="Drag point",
                narration="Keep investing regularly.",
            )
        ],
    )
    # Plan with hook_plan=None (legacy plan)
    comp_plan = FullCompositionPlan(
        thesis="Inflation destroys cash.",
        visual_mode="composition",
        hook_plan=None,
        ideas=[
            IdeaCompositionPlan(
                idea_id="idea_01",
                narration="Keep investing regularly.",
                beats=[
                    CompositionBeat(
                        beat_id="beat_01_01",
                        composition_id="broll_caption",
                        variant="statement",
                        composition_data={"caption": "Keep investing regularly."},
                        trigger_word=None,
                    )
                ],
            )
        ],
    )

    voice_track = VoiceTrack(
        voice_id="Joanna",
        audio_file_name="audio.mp3",
        storage_key="audio.mp3",
        duration_seconds=4.0,
        full_script_text="Imagine losing 40% of wealth. Keep investing regularly.",
        word_timestamps=[
            WordTimestamp(word="Imagine", start_ms=0, end_ms=1800),
            WordTimestamp(word="Keep", start_ms=1900, end_ms=3800),
        ],
    )

    engine = CompositionAssemblyEngine(fps=30)
    render_spec = engine.run(
        scene_id="test_scene",
        hook=hook,
        strategy=strategy,
        composition_plan=comp_plan,
        voice_track=voice_track,
    )

    scenes = render_spec.props.scenes
    # Hook scene: falls back to legacy Typography without error
    assert scenes[0].component.component_id == "Typography"
    assert scenes[0].component.props["text"] == "Legacy Fallback Text"
