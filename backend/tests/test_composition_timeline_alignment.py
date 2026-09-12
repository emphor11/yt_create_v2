"""
Tests for composition-mode timeline and beat alignment.

Verifies:
1. 1 intent -> 1 composition beat (spans entire idea without trigger word).
2. 1 intent -> 2 composition beats (partitions cleanly on trigger word).
3. Multiple ideas with variable beat counts (e.g. 1 beat, 2 beats, 3 beats).
4. Exact contiguous timing and final-duration behavior.
5. Zero legacy component resolution in composition body scenes.
6. Legacy mode remains 100% backward compatible when composition_plan is None.
"""
import pytest
from domain.hook import Hook, VisualDirective as HookVisualDirective
from domain.script_visual_strategy import ScriptVisualStrategy, VideoIdea, VisualStrategyBeat
from domain.composition_plan import FullCompositionPlan, IdeaCompositionPlan, CompositionBeat
from domain.voice_track import VoiceTrack, WordTimestamp
from engines.video_assembly.timeline_builder import TimelineBuilder
from engines.composition_assembly_engine import CompositionAssemblyEngine


def make_test_voice_track() -> VoiceTrack:
    """Creates a 10-second voice track with word timestamps for hook and 3 ideas."""
    words = [
        # Hook (0-2000ms)
        WordTimestamp(word="Stop", start_ms=0, end_ms=400),
        WordTimestamp(word="ignoring", start_ms=500, end_ms=900),
        WordTimestamp(word="your", start_ms=1000, end_ms=1300),
        WordTimestamp(word="money", start_ms=1400, end_ms=1900),
        # Idea 1 (2000-4000ms)
        WordTimestamp(word="Saving", start_ms=2100, end_ms=2500),
        WordTimestamp(word="ten", start_ms=2600, end_ms=2900),
        WordTimestamp(word="lakh", start_ms=3000, end_ms=3400),
        WordTimestamp(word="matters", start_ms=3500, end_ms=3900),
        # Idea 2 (4000-7000ms)
        WordTimestamp(word="When", start_ms=4100, end_ms=4400),
        WordTimestamp(word="compounding", start_ms=4500, end_ms=5000),
        WordTimestamp(word="begins", start_ms=5100, end_ms=5400),
        WordTimestamp(word="growth", start_ms=5600, end_ms=6000),
        WordTimestamp(word="becomes", start_ms=6100, end_ms=6500),
        WordTimestamp(word="automatic", start_ms=6600, end_ms=6900),
        # Idea 3 (7000-10000ms)
        WordTimestamp(word="First", start_ms=7100, end_ms=7400),
        WordTimestamp(word="decade", start_ms=7500, end_ms=7900),
        WordTimestamp(word="is", start_ms=8000, end_ms=8200),
        WordTimestamp(word="effort", start_ms=8300, end_ms=8700),
        WordTimestamp(word="second", start_ms=8900, end_ms=9300),
        WordTimestamp(word="momentum", start_ms=9400, end_ms=9900),
    ]
    return VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="test/narration.mp3",
        duration_seconds=10.0,
        full_script_text="Stop ignoring your money. Saving ten lakh matters. When compounding begins growth becomes automatic. First decade is effort second momentum.",
        word_timestamps=words,
    )


def make_test_hook() -> Hook:
    return Hook(
        conceptual_hook="Attention Grabber",
        script_text="Stop ignoring your money.",
        visual_directives=[
            HookVisualDirective(beat_id="hook_b1", preferred_component="Typography", visual_instruction="Title", trigger_word=None),
            HookVisualDirective(beat_id="hook_b2", preferred_component="Typography", visual_instruction="Subtitle", trigger_word="money"),
        ],
    )


def make_legacy_strategy() -> ScriptVisualStrategy:
    """Legacy strategy with strict 2 beats per idea."""
    return ScriptVisualStrategy(
        thesis="Wealth Building",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Milestone 1",
                focus_concept="Ten Lakh",
                core_teaching_point="Hardest part",
                narration="Saving ten lakh matters.",
                visual_sequence=[
                    VisualStrategyBeat(beat_id="leg_1_1", preferred_component="Typography", visual_goal="Goal 1", trigger_word=None),
                    VisualStrategyBeat(beat_id="leg_1_2", preferred_component="Typography", visual_goal="Goal 2", trigger_word="matters"),
                ],
            ),
            VideoIdea(
                idea_id="idea_02",
                title="Compounding",
                focus_concept="Auto growth",
                core_teaching_point="Math flips",
                narration="When compounding begins growth becomes automatic.",
                visual_sequence=[
                    VisualStrategyBeat(beat_id="leg_2_1", preferred_component="Typography", visual_goal="Goal 3", trigger_word=None),
                    VisualStrategyBeat(beat_id="leg_2_2", preferred_component="Typography", visual_goal="Goal 4", trigger_word="automatic"),
                ],
            ),
            VideoIdea(
                idea_id="idea_03",
                title="Time Horizon",
                focus_concept="Momentum",
                core_teaching_point="Decades",
                narration="First decade is effort second momentum.",
                visual_sequence=[
                    VisualStrategyBeat(beat_id="leg_3_1", preferred_component="Typography", visual_goal="Goal 5", trigger_word=None),
                    VisualStrategyBeat(beat_id="leg_3_2", preferred_component="Typography", visual_goal="Goal 6", trigger_word="momentum"),
                ],
            ),
        ],
    )


# --- 1. Single beat per idea spans entire idea interval ---

def test_composition_timeline_single_beat_spans_entire_idea():
    builder = TimelineBuilder(fps=30)
    hook = make_test_hook()
    strategy = make_legacy_strategy()
    voice_track = make_test_voice_track()

    # Idea 1 has exactly 1 beat
    comp_plan = FullCompositionPlan(
        thesis="Wealth Building",
        visual_mode="composition",
        ideas=[
            IdeaCompositionPlan(
                idea_id="idea_01",
                narration="Saving ten lakh matters.",
                beats=[
                    CompositionBeat(
                        beat_id="comp_1_1",
                        composition_id="metric_hero",
                        composition_data={"value": "₹10 lakh", "label": "Milestone"},
                        trigger_word=None,
                        visual_goal="Show 10 lakh",
                    ),
                ],
            ),
        ],
    )

    timeline = builder.build_timeline(
        hook=hook,
        strategy=strategy,
        voice_track=voice_track,
        composition_plan=comp_plan,
    )

    # 2 hook beats + 1 composition beat = 3 total intervals
    assert len(timeline) == 3
    assert timeline[0].beat_id == "hook_b1"
    assert timeline[1].beat_id == "hook_b2"
    assert timeline[2].beat_id == "comp_1_1"
    assert timeline[2].section_type == "body"
    assert timeline[2].section_index == 0
    assert timeline[2].beat_index == 0

    # Ensure contiguous coverage to end
    assert timeline[0].start_frame == 0
    assert timeline[1].start_frame == timeline[0].end_frame
    assert timeline[2].start_frame == timeline[1].end_frame
    assert timeline[2].end_frame == 300  # 10s * 30fps


# --- 2. Multiple beats partition cleanly on trigger word ---

def test_composition_timeline_two_beats_partition_cleanly():
    builder = TimelineBuilder(fps=30)
    hook = make_test_hook()
    strategy = make_legacy_strategy()
    voice_track = make_test_voice_track()

    # Idea 2 has 2 composition beats: beat 2 triggered by "automatic"
    comp_plan = FullCompositionPlan(
        thesis="Wealth Building",
        visual_mode="composition",
        ideas=[
            IdeaCompositionPlan(
                idea_id="idea_02",
                narration="When compounding begins growth becomes automatic.",
                beats=[
                    CompositionBeat(
                        beat_id="comp_2_1",
                        composition_id="calculation_story",
                        composition_data={
                            "input_label": "Savings", "input_value": "₹10L",
                            "operation_label": "×", "rate_label": "12%",
                            "result_label": "Returns", "result_value": "₹1.2L",
                        },
                        trigger_word=None,
                        visual_goal="Show math",
                    ),
                    CompositionBeat(
                        beat_id="comp_2_2",
                        composition_id="broll_caption",
                        composition_data={"caption": "Growth is automatic"},
                        trigger_word="automatic",
                        visual_goal="Show momentum",
                    ),
                ],
            ),
        ],
    )

    timeline = builder.build_timeline(
        hook=hook,
        strategy=strategy,
        voice_track=voice_track,
        composition_plan=comp_plan,
    )

    assert len(timeline) == 4  # 2 hook beats + 2 composition beats
    assert timeline[2].beat_id == "comp_2_1"
    assert timeline[3].beat_id == "comp_2_2"
    # Beat 2 starts after beat 1
    assert timeline[3].start_frame > timeline[2].start_frame
    assert timeline[2].end_frame == timeline[3].start_frame
    assert timeline[3].end_frame == 300


# --- 3. Variable beat counts across ideas ---

def test_composition_timeline_variable_beats_across_ideas():
    builder = TimelineBuilder(fps=30)
    hook = make_test_hook()
    strategy = make_legacy_strategy()
    voice_track = make_test_voice_track()

    # Idea 1: 1 beat, Idea 2: 2 beats, Idea 3: 3 beats
    comp_plan = FullCompositionPlan(
        thesis="Wealth Building",
        visual_mode="composition",
        ideas=[
            IdeaCompositionPlan(
                idea_id="idea_01",
                narration="Saving ten lakh matters.",
                beats=[
                    CompositionBeat(
                        beat_id="comp_1_1",
                        composition_id="metric_hero",
                        composition_data={"value": "₹10 lakh", "label": "Milestone"},
                    ),
                ],
            ),
            IdeaCompositionPlan(
                idea_id="idea_02",
                narration="When compounding begins growth becomes automatic.",
                beats=[
                    CompositionBeat(
                        beat_id="comp_2_1",
                        composition_id="calculation_story",
                        composition_data={
                            "input_label": "A", "input_value": "1",
                            "operation_label": "×", "rate_label": "2",
                            "result_label": "C", "result_value": "2",
                        },
                    ),
                    CompositionBeat(
                        beat_id="comp_2_2",
                        composition_id="broll_caption",
                        composition_data={"caption": "Automatic growth"},
                        trigger_word="growth",
                    ),
                ],
            ),
            IdeaCompositionPlan(
                idea_id="idea_03",
                narration="First decade is effort second momentum.",
                beats=[
                    CompositionBeat(
                        beat_id="comp_3_1",
                        composition_id="time_decay",
                        composition_data={
                            "fixed_amount": "₹10L", "amount_label": "Value",
                            "time_period": "10y", "emphasis": "value_erosion",
                        },
                    ),
                    CompositionBeat(
                        beat_id="comp_3_2",
                        composition_id="cause_effect",
                        composition_data={
                            "causes": [{"label": "Discipline"}],
                            "connector": "leads to", "outcome_label": "Wealth",
                        },
                        trigger_word="effort",
                    ),
                    CompositionBeat(
                        beat_id="comp_3_3",
                        composition_id="broll_caption",
                        composition_data={"caption": "Momentum carries you"},
                        trigger_word="momentum",
                    ),
                ],
            ),
        ],
    )

    timeline = builder.build_timeline(
        hook=hook,
        strategy=strategy,
        voice_track=voice_track,
        composition_plan=comp_plan,
    )

    # 2 hook beats + 1 + 2 + 3 = 8 total intervals
    assert len(timeline) == 8
    expected_beat_ids = [
        "hook_b1", "hook_b2",
        "comp_1_1",
        "comp_2_1", "comp_2_2",
        "comp_3_1", "comp_3_2", "comp_3_3",
    ]
    actual_beat_ids = [t.beat_id for t in timeline]
    assert actual_beat_ids == expected_beat_ids

    # Contiguity check
    for i in range(1, len(timeline)):
        assert timeline[i].start_frame == timeline[i - 1].end_frame
    assert timeline[0].start_frame == 0
    assert timeline[-1].end_frame == 300


# --- 4. Assembly engine: zero legacy component resolution in composition body ---

def test_composition_assembly_zero_legacy_components_in_body():
    hook = make_test_hook()
    strategy = make_legacy_strategy()  # legacy visual_sequence has 2 beats per idea
    voice_track = make_test_voice_track()

    # Composition plan has asymmetric beats: Idea 1 has 1 beat, Idea 2 has 1 beat, Idea 3 has 2 beats
    comp_plan = FullCompositionPlan(
        thesis="Wealth Building",
        visual_mode="composition",
        ideas=[
            IdeaCompositionPlan(
                idea_id="idea_01",
                narration="Saving ten lakh matters.",
                beats=[
                    CompositionBeat(
                        beat_id="comp_1_1",
                        composition_id="metric_hero",
                        composition_data={"value": "₹10 lakh", "label": "Milestone"},
                    ),
                ],
            ),
            IdeaCompositionPlan(
                idea_id="idea_02",
                narration="When compounding begins growth becomes automatic.",
                beats=[
                    CompositionBeat(
                        beat_id="comp_2_1",
                        composition_id="calculation_story",
                        composition_data={
                            "input_label": "A", "input_value": "1",
                            "operation_label": "×", "rate_label": "2",
                            "result_label": "C", "result_value": "2",
                        },
                    ),
                ],
            ),
            IdeaCompositionPlan(
                idea_id="idea_03",
                narration="First decade is effort second momentum.",
                beats=[
                    CompositionBeat(
                        beat_id="comp_3_1",
                        composition_id="time_decay",
                        composition_data={
                            "fixed_amount": "₹10L", "amount_label": "Value",
                            "time_period": "10y", "emphasis": "value_erosion",
                        },
                    ),
                    CompositionBeat(
                        beat_id="comp_3_2",
                        composition_id="broll_caption",
                        composition_data={"caption": "Momentum carries you"},
                        trigger_word="momentum",
                    ),
                ],
            ),
        ],
    )

    assembly_engine = CompositionAssemblyEngine(fps=30)
    render_spec = assembly_engine.run(
        scene_id="scene_test_zero_legacy",
        hook=hook,
        strategy=strategy,
        composition_plan=comp_plan,
        voice_track=voice_track,
    )

    scenes = render_spec.props.scenes
    # Hook: 2 scenes (indices 0, 1)
    # Body: 4 scenes (indices 2, 3, 4, 5) -> metric_hero, calculation_story, time_decay, broll_caption
    assert len(scenes) == 6

    body_scenes = scenes[2:]
    body_components = [s.component.component_id for s in body_scenes]

    # Must match the composition Remotion components exactly
    assert body_components == [
        "MetricHero",
        "CalculationStory",
        "TimeDecay",
        "BrollCaption",
    ]

    # Explicitly ensure NO legacy Typography, NumberCounter, StockVideo, etc. leaked into body
    legacy_components = {"Typography", "NumberCounter", "StockVideo", "StockImage", "ProcessFlow", "SplitComparison"}
    for comp in body_components:
        assert comp not in legacy_components, f"Accidental legacy component '{comp}' found in composition body!"


# --- 5. Legacy mode behavior unchanged when composition_plan is None ---

def test_legacy_timeline_builder_remains_unchanged():
    builder = TimelineBuilder(fps=30)
    hook = make_test_hook()
    strategy = make_legacy_strategy()
    voice_track = make_test_voice_track()

    # Calling build_timeline without composition_plan
    timeline = builder.build_timeline(
        hook=hook,
        strategy=strategy,
        voice_track=voice_track,
    )

    # 2 hook beats + 3 ideas * 2 beats = 8 intervals
    assert len(timeline) == 8
    expected_legacy_beat_ids = [
        "hook_b1", "hook_b2",
        "leg_1_1", "leg_1_2",
        "leg_2_1", "leg_2_2",
        "leg_3_1", "leg_3_2",
    ]
    actual_beat_ids = [t.beat_id for t in timeline]
    assert actual_beat_ids == expected_legacy_beat_ids
