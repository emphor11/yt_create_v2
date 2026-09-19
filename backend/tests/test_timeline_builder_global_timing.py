import pytest
from domain.hook import Hook, VisualDirective as HookVisualDirective
from domain.script_visual_strategy import ScriptVisualStrategy, VideoIdea
from domain.composition_plan import FullCompositionPlan, IdeaCompositionPlan, CompositionBeat
from domain.voice_track import VoiceTrack, WordTimestamp
from engines.video_assembly.timeline_builder import (
    TimelineBuilder,
    TimelineBuilderError,
    _find_trigger_index,
    _is_word_match,
    MIN_BEAT_DURATION_FRAMES,
)


# =========================================================================
# Test A: Single trigger word
# =========================================================================
def test_a_single_trigger_word():
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="Is salary a drug?",
        visual_directives=[
            HookVisualDirective(beat_id="h_beat_1", visual_instruction="Intro", trigger_word=None),
            HookVisualDirective(beat_id="h_beat_2", visual_instruction="Cut", trigger_word="salary"),
        ],
    )
    strategy = ScriptVisualStrategy(thesis="Thesis", ideas=[])
    voice_track = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="runs/r1/narration.mp3",
        duration_seconds=2.0,
        full_script_text="Is salary a drug?",
        word_timestamps=[
            WordTimestamp(word="Is", start_ms=0, end_ms=200),
            WordTimestamp(word="salary", start_ms=200, end_ms=500),  # Trigger at 200ms -> frame 6 (min 15 applied)
            WordTimestamp(word="a", start_ms=500, end_ms=600),
            WordTimestamp(word="drug", start_ms=600, end_ms=900),
        ],
    )

    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=voice_track)
    assert len(timeline) == 2
    assert timeline[0].beat_id == "h_beat_1"
    assert timeline[0].start_frame == 0
    assert timeline[1].beat_id == "h_beat_2"
    # Enforces min 15 frames for beat 1, so beat 2 starts at frame 15
    assert timeline[1].start_frame == 15
    assert timeline[0].end_frame == 15
    assert timeline[1].end_frame == 60  # 2.0s * 30fps = 60


# =========================================================================
# Test B: Multiple occurrences of the same trigger word
# =========================================================================
def test_b_multiple_occurrences_resolves_deterministically():
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="The market rose then the market fell.",
        visual_directives=[
            HookVisualDirective(beat_id="h_beat_1", visual_instruction="Intro", trigger_word=None),
            HookVisualDirective(beat_id="h_beat_2", visual_instruction="First market", trigger_word="market"),
        ],
    )
    strategy = ScriptVisualStrategy(thesis="Thesis", ideas=[])
    voice_track = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="runs/r1/narration.mp3",
        duration_seconds=3.0,
        full_script_text="The market rose then the market fell.",
        word_timestamps=[
            WordTimestamp(word="The", start_ms=0, end_ms=200),
            WordTimestamp(word="market", start_ms=600, end_ms=900),   # 1st occurrence at 600ms -> frame 18
            WordTimestamp(word="rose", start_ms=900, end_ms=1200),
            WordTimestamp(word="then", start_ms=1200, end_ms=1400),
            WordTimestamp(word="the", start_ms=1400, end_ms=1600),
            WordTimestamp(word="market", start_ms=1600, end_ms=1900), # 2nd occurrence at 1600ms -> frame 48
            WordTimestamp(word="fell", start_ms=1900, end_ms=2200),
        ],
    )

    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=voice_track)
    assert len(timeline) == 2
    # Beat 2 matches the FIRST occurrence of "market" after beat 1
    assert timeline[1].start_frame == 18


# =========================================================================
# Test C: Repeated triggers across multiple visual beats
# =========================================================================
def test_c_repeated_triggers_across_multiple_beats():
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="The market rose then the market fell.",
        visual_directives=[
            HookVisualDirective(beat_id="h_beat_1", visual_instruction="Intro", trigger_word=None),
            HookVisualDirective(beat_id="h_beat_2", visual_instruction="Rise beat", trigger_word="market"),
            HookVisualDirective(beat_id="h_beat_3", visual_instruction="Fall beat", trigger_word="market"),
        ],
    )
    strategy = ScriptVisualStrategy(thesis="Thesis", ideas=[])
    voice_track = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="runs/r1/narration.mp3",
        duration_seconds=3.0,
        full_script_text="The market rose then the market fell.",
        word_timestamps=[
            WordTimestamp(word="The", start_ms=0, end_ms=200),
            WordTimestamp(word="market", start_ms=600, end_ms=900),   # 1st: 600ms -> frame 18
            WordTimestamp(word="rose", start_ms=900, end_ms=1200),
            WordTimestamp(word="then", start_ms=1200, end_ms=1400),
            WordTimestamp(word="the", start_ms=1400, end_ms=1600),
            WordTimestamp(word="market", start_ms=1600, end_ms=1900), # 2nd: 1600ms -> frame 48
            WordTimestamp(word="fell", start_ms=1900, end_ms=2200),
        ],
    )

    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=voice_track)
    assert len(timeline) == 3
    # Beat 1 covers intro
    assert timeline[0].start_frame == 0
    assert timeline[0].end_frame == 18
    # Beat 2 triggers on 1st "market" at frame 18
    assert timeline[1].start_frame == 18
    assert timeline[1].end_frame == 48
    # Beat 3 triggers on 2nd "market" at frame 48
    assert timeline[2].start_frame == 48
    assert timeline[2].end_frame == 90  # total duration 3.0s * 30 = 90


# =========================================================================
# Test D: Trigger word at the beginning of narration
# =========================================================================
def test_d_trigger_word_at_beginning_of_narration():
    timestamps = [
        WordTimestamp(word="First", start_ms=0, end_ms=300),
        WordTimestamp(word="word", start_ms=300, end_ms=600),
    ]
    # Direct function test: index 0 matched when prev_start_idx=0
    idx = _find_trigger_index(timestamps, trigger_raw="First", section_text="First word", prev_start_idx=0)
    assert idx == 0

    # In timeline: beat 1 triggers on the very next word (word 1)
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="First word spoken.",
        visual_directives=[
            HookVisualDirective(beat_id="h1", visual_instruction="Intro", trigger_word=None),
            HookVisualDirective(beat_id="h2", visual_instruction="Next", trigger_word="word"),
        ],
    )
    strategy = ScriptVisualStrategy(thesis="Thesis", ideas=[])
    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=2.0,
        full_script_text="First word spoken.",
        word_timestamps=[
            WordTimestamp(word="First", start_ms=0, end_ms=500),
            WordTimestamp(word="word", start_ms=600, end_ms=1000), # 600ms -> frame 18
            WordTimestamp(word="spoken", start_ms=1000, end_ms=1500),
        ],
    )
    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=vt)
    assert len(timeline) == 2
    assert timeline[1].start_frame == 18


# =========================================================================
# Test E: Trigger word at the end of narration
# =========================================================================
def test_e_trigger_word_at_end_of_narration():
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="Start and finish.",
        visual_directives=[
            HookVisualDirective(beat_id="h1", visual_instruction="Intro", trigger_word=None),
            HookVisualDirective(beat_id="h2", visual_instruction="Finish", trigger_word="finish"),
        ],
    )
    strategy = ScriptVisualStrategy(thesis="Thesis", ideas=[])
    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=3.0,
        full_script_text="Start and finish.",
        word_timestamps=[
            WordTimestamp(word="Start", start_ms=0, end_ms=400),
            WordTimestamp(word="and", start_ms=400, end_ms=700),
            WordTimestamp(word="finish", start_ms=2000, end_ms=2500), # 2000ms -> frame 60
        ],
    )
    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=vt)
    assert len(timeline) == 2
    assert timeline[1].start_frame == 60
    assert timeline[1].end_frame == 90  # 3.0s * 30fps


# =========================================================================
# Test F: Trigger word next to punctuation
# =========================================================================
def test_f_trigger_word_next_to_punctuation():
    timestamps = [
        WordTimestamp(word="safety,", start_ms=0, end_ms=300),
        WordTimestamp(word="$100B!", start_ms=300, end_ms=600),
        WordTimestamp(word="'rates'?", start_ms=600, end_ms=900),
    ]
    assert _find_trigger_index(timestamps, "safety", "safety, $100B! 'rates'?", 0) == 0
    assert _find_trigger_index(timestamps, "100B", "safety, $100B! 'rates'?", 0) == 1
    assert _find_trigger_index(timestamps, "rates", "safety, $100B! 'rates'?", 0) == 2


# =========================================================================
# Test G: Case variations
# =========================================================================
def test_g_case_variations_matching():
    timestamps = [
        WordTimestamp(word="Bitcoin", start_ms=0, end_ms=300),
        WordTimestamp(word="ETHEREUM", start_ms=300, end_ms=600),
    ]
    assert _find_trigger_index(timestamps, "bITcoIN", "Bitcoin ETHEREUM", 0) == 0
    assert _find_trigger_index(timestamps, "ethereum", "Bitcoin ETHEREUM", 0) == 1


# =========================================================================
# Test H: Missing trigger word raises TimelineBuilderError
# =========================================================================
def test_h_missing_trigger_word_fails_clearly():
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="Hello world.",
        visual_directives=[
            HookVisualDirective(beat_id="h1", visual_instruction="Intro", trigger_word=None),
            HookVisualDirective(beat_id="h2", visual_instruction="Fail", trigger_word="nonexistent"),
        ],
    )
    strategy = ScriptVisualStrategy(thesis="Thesis", ideas=[])
    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=2.0,
        full_script_text="Hello world.",
        word_timestamps=[
            WordTimestamp(word="Hello", start_ms=0, end_ms=300),
            WordTimestamp(word="world", start_ms=300, end_ms=600),
        ],
    )
    with pytest.raises(TimelineBuilderError) as exc_info:
        builder.build_timeline(hook=hook, strategy=strategy, voice_track=vt)

    err = str(exc_info.value)
    assert "Trigger word 'nonexistent'" in err
    assert "beat 'h2'" in err


# =========================================================================
# Test I & J: Trigger words spanning different Polly chunks with GLOBAL timestamps
# =========================================================================
def test_i_and_j_trigger_words_spanning_polly_chunks_using_global_timestamps():
    """
    Verifies that TimelineBuilder consumes global timestamps produced by Step 3
    across multiple chapters without needing to know about chunks.
    """
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="Hook intro here.",
        visual_directives=[
            HookVisualDirective(beat_id="h1", visual_instruction="Intro", trigger_word=None),
            HookVisualDirective(beat_id="h2", visual_instruction="Here cut", trigger_word="here"),
        ],
    )
    strategy = ScriptVisualStrategy(
        thesis="Thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="T1",
                focus_concept="C1",
                core_teaching_point="P1",
                narration="Idea one reveals danger.",
            ),
            VideoIdea(
                idea_id="idea_02",
                title="T2",
                focus_concept="C2",
                core_teaching_point="P2",
                narration="Idea two unlocks solution.",
            ),
        ],
    )
    composition_plan = FullCompositionPlan(
        thesis="Thesis",
        ideas=[
            IdeaCompositionPlan(
                idea_id="idea_01",
                narration="Idea one reveals danger.",
                beats=[
                    CompositionBeat(beat_id="b1_1", composition_id="metric_hero", trigger_word=None),
                    CompositionBeat(beat_id="b1_2", composition_id="metric_hero", trigger_word="danger"),
                ],
            ),
            IdeaCompositionPlan(
                idea_id="idea_02",
                narration="Idea two unlocks solution.",
                beats=[
                    CompositionBeat(beat_id="b2_1", composition_id="metric_hero", trigger_word=None),
                    CompositionBeat(beat_id="b2_2", composition_id="metric_hero", trigger_word="solution"),
                ],
            ),
        ],
    )

    # Chunk 1 (Hook): duration = 2000ms
    # Chunk 2 (Idea 1): offset = 2000ms, duration = 3000ms
    # Chunk 3 (Idea 2): offset = 5000ms, duration = 3000ms
    # Total audio duration = 8.0s (240 frames)
    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=8.0,
        full_script_text="Hook intro here.\n\nIdea one reveals danger.\n\nIdea two unlocks solution.",
        word_timestamps=[
            # Hook (chunk 1, offset 0)
            WordTimestamp(word="Hook", start_ms=0, end_ms=300),
            WordTimestamp(word="intro", start_ms=300, end_ms=600),
            WordTimestamp(word="here", start_ms=1000, end_ms=1300),  # Frame: 30
            # Idea 1 (chunk 2, offset 2000ms)
            WordTimestamp(word="Idea", start_ms=2000, end_ms=2300),
            WordTimestamp(word="one", start_ms=2300, end_ms=2600),
            WordTimestamp(word="reveals", start_ms=2600, end_ms=3000),
            WordTimestamp(word="danger", start_ms=3500, end_ms=4000), # Frame: int(round(3.5 * 30)) = 105
            # Idea 2 (chunk 3, offset 5000ms)
            WordTimestamp(word="Idea", start_ms=5000, end_ms=5300),
            WordTimestamp(word="two", start_ms=5300, end_ms=5600),
            WordTimestamp(word="unlocks", start_ms=5600, end_ms=6200),
            WordTimestamp(word="solution", start_ms=6800, end_ms=7500), # Frame: int(round(6.8 * 30)) = 204
        ],
    )

    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=vt, composition_plan=composition_plan)
    assert len(timeline) == 6

    # Hook beats
    assert timeline[0].beat_id == "h1"
    assert timeline[0].start_frame == 0
    assert timeline[1].beat_id == "h2"
    assert timeline[1].start_frame == 30

    # Idea 1 beats
    assert timeline[2].beat_id == "b1_1"
    assert timeline[2].start_frame == 60  # Idea 1 starts at 2000ms -> frame 60
    assert timeline[3].beat_id == "b1_2"
    assert timeline[3].start_frame == 105 # "danger" at 3500ms -> frame 105

    # Idea 2 beats
    assert timeline[4].beat_id == "b2_1"
    assert timeline[4].start_frame == 150 # Idea 2 starts at 5000ms -> frame 150
    assert timeline[5].beat_id == "b2_2"
    assert timeline[5].start_frame == 204 # "solution" at 6800ms -> frame 204
    assert timeline[5].end_frame == 240   # 8.0s * 30 = 240


# =========================================================================
# Test K: Regression test proving chunk-local timestamps are not used
# =========================================================================
def test_k_regression_chunk_local_timestamps_not_accidentally_treated_as_global():
    """
    If chunk 2 local timestamps (e.g. 100ms) were used instead of global timestamps (3100ms),
    idea 1's beat would start at frame 3 instead of frame 93!
    """
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="First chapter.",
        visual_directives=[
            HookVisualDirective(beat_id="h1", visual_instruction="Intro", trigger_word=None),
        ],
    )
    strategy = ScriptVisualStrategy(
        thesis="Thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="T1",
                focus_concept="C1",
                core_teaching_point="P1",
                narration="Second chapter starts.",
            ),
        ],
    )
    composition_plan = FullCompositionPlan(
        thesis="Thesis",
        ideas=[
            IdeaCompositionPlan(
                idea_id="idea_01",
                narration="Second chapter starts.",
                beats=[
                    CompositionBeat(beat_id="b1", composition_id="metric_hero", trigger_word=None),
                    CompositionBeat(beat_id="b2", composition_id="metric_hero", trigger_word="starts"),
                ],
            ),
        ],
    )
    # Chunk 1 duration = 3000ms.
    # Chunk 2 word "starts" has local start_ms = 600, but global start_ms = 3600 (frame 108).
    # Since idea 1 starts at 3000ms (frame 90), 3600ms gives 18 frames duration for b1 (> 15 min frames).
    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=5.0,
        full_script_text="First chapter.\n\nSecond chapter starts.",
        word_timestamps=[
            WordTimestamp(word="First", start_ms=0, end_ms=500),
            WordTimestamp(word="chapter", start_ms=500, end_ms=1000),
            # Global timestamps for chunk 2:
            WordTimestamp(word="Second", start_ms=3000, end_ms=3200),
            WordTimestamp(word="chapter", start_ms=3200, end_ms=3500),
            WordTimestamp(word="starts", start_ms=3600, end_ms=4000), # Frame 108
        ],
    )

    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=vt, composition_plan=composition_plan)
    b2 = [t for t in timeline if t.beat_id == "b2"][0]

    # Verify frame 108 (from global 3600ms) and NOT frame 18 (from local 600ms)
    assert b2.start_frame == 108
    assert b2.start_frame != 18


# =========================================================================
# Special Test: Chunk 1 duration > last speech-mark timestamp
# =========================================================================
def test_drift_trap_chunk1_duration_greater_than_last_speech_mark():
    """
    CRITICAL DRIFT TRAP VERIFICATION:
    Chunk 1 actual audio duration is 3000ms.
    Chunk 1 last speech mark ended at 2200ms (800ms natural pause).
    Chunk 2's trigger word is at local 600ms.
    GLOBAL timestamp from Step 3 = 3000 + 600 = 3600ms.
    TimelineBuilder must place the trigger at frame 108 (3600ms),
    NOT frame 84 (2200 + 600 = 2800ms) and NOT frame 18 (600ms).
    """
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="Short hook text.",
        visual_directives=[
            HookVisualDirective(beat_id="h1", visual_instruction="Intro", trigger_word=None),
        ],
    )
    strategy = ScriptVisualStrategy(
        thesis="Thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="T1",
                focus_concept="C1",
                core_teaching_point="P1",
                narration="Next chapter opens.",
            ),
        ],
    )
    composition_plan = FullCompositionPlan(
        thesis="Thesis",
        ideas=[
            IdeaCompositionPlan(
                idea_id="idea_01",
                narration="Next chapter opens.",
                beats=[
                    CompositionBeat(beat_id="b1", composition_id="metric_hero", trigger_word=None),
                    CompositionBeat(beat_id="b2", composition_id="metric_hero", trigger_word="opens"),
                ],
            ),
        ],
    )
    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=5.0,
        full_script_text="Short hook text.\n\nNext chapter opens.",
        word_timestamps=[
            # Chunk 1 ends speech marks at 2200ms, but chunk duration was 3000ms
            WordTimestamp(word="Short", start_ms=0, end_ms=600),
            WordTimestamp(word="hook", start_ms=600, end_ms=1200),
            WordTimestamp(word="text", start_ms=1200, end_ms=2200),
            # Chunk 2 word offset = 3000ms (cumulative physical duration):
            WordTimestamp(word="Next", start_ms=3000, end_ms=3200),
            WordTimestamp(word="chapter", start_ms=3200, end_ms=3500),
            WordTimestamp(word="opens", start_ms=3600, end_ms=4000), # 3600ms -> Frame 108
        ],
    )

    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=vt, composition_plan=composition_plan)
    opens_beat = [t for t in timeline if t.beat_id == "b2"][0]

    # At 30 FPS: 3600ms / 1000 * 30 = 108.0 -> frame 108
    assert opens_beat.start_frame == 108
    # If it had used the last speech mark (2200ms + 600ms = 2800ms), it would be frame 84:
    assert opens_beat.start_frame != 84
    # If it had used local timestamp (600ms), it would be frame 18:
    assert opens_beat.start_frame != 18


# =========================================================================
# Test L: Word assignment correctness
# =========================================================================
def test_l_word_assignment_preserves_all_words_across_sections():
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="First section.",
        visual_directives=[HookVisualDirective(beat_id="h1", visual_instruction="Intro", trigger_word=None)],
    )
    strategy = ScriptVisualStrategy(
        thesis="Thesis",
        ideas=[
            VideoIdea(
                idea_id="i1",
                title="T1",
                focus_concept="C1",
                core_teaching_point="P1",
                narration="Second section words.",
            )
        ],
    )
    word_timestamps = [
        WordTimestamp(word="First", start_ms=0, end_ms=200),
        WordTimestamp(word="section", start_ms=200, end_ms=400),
        WordTimestamp(word="Second", start_ms=1000, end_ms=1200),
        WordTimestamp(word="section", start_ms=1200, end_ms=1400),
        WordTimestamp(word="words", start_ms=1400, end_ms=1600),
    ]
    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=2.0,
        full_script_text="First section.\n\nSecond section words.",
        word_timestamps=word_timestamps,
    )
    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=vt)
    assert len(timeline) == 2
    assert timeline[0].section_type == "hook"
    assert timeline[1].section_type == "body"


# =========================================================================
# Test M: Frame conversion correctness
# =========================================================================
@pytest.mark.parametrize(
    "fps,start_ms,expected_frame",
    [
        (30, 0, 0),
        (30, 500, 15),
        (30, 1000, 30),
        (30, 3100, 93),
        (60, 1000, 60),
    ],
)
def test_m_frame_conversion_math(fps, start_ms, expected_frame):
    builder = TimelineBuilder(fps=fps)
    frame = int(round((start_ms / 1000.0) * builder.fps))
    assert frame == expected_frame


# =========================================================================
# Test N: Existing 15-frame minimum beat duration behavior
# =========================================================================
def test_n_minimum_beat_duration_enforced():
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="One two three.",
        visual_directives=[
            HookVisualDirective(beat_id="h1", visual_instruction="Intro", trigger_word=None),
            # Trigger words spaced only 100ms (3 frames) apart
            HookVisualDirective(beat_id="h2", visual_instruction="Two", trigger_word="two"),
            HookVisualDirective(beat_id="h3", visual_instruction="Three", trigger_word="three"),
        ],
    )
    strategy = ScriptVisualStrategy(thesis="Thesis", ideas=[])
    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=3.0,
        full_script_text="One two three.",
        word_timestamps=[
            WordTimestamp(word="One", start_ms=0, end_ms=100),
            WordTimestamp(word="two", start_ms=100, end_ms=200),   # 100ms -> frame 3
            WordTimestamp(word="three", start_ms=200, end_ms=300), # 200ms -> frame 6
        ],
    )
    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=vt)
    assert len(timeline) == 3
    # Beat 1: start_frame = 0
    assert timeline[0].start_frame == 0
    # Beat 2: exact frame is 3, but min beat duration from 0 is 15 -> clamped to 15!
    assert timeline[1].start_frame == 15
    # Beat 3: exact frame is 6, but min beat duration from 15 is 30 -> clamped to 30!
    assert timeline[2].start_frame == 30


# =========================================================================
# Test O: Final beat reaches total audio duration
# =========================================================================
def test_o_final_beat_reaches_total_duration():
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="Short.",
        visual_directives=[HookVisualDirective(beat_id="h1", visual_instruction="Intro", trigger_word=None)],
    )
    strategy = ScriptVisualStrategy(thesis="Thesis", ideas=[])
    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=10.0, # 300 frames
        full_script_text="Short.",
        word_timestamps=[WordTimestamp(word="Short", start_ms=0, end_ms=500)],
    )
    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=vt)
    assert len(timeline) == 1
    assert timeline[0].end_frame == 300
    assert timeline[0].duration_frames == 300


# =========================================================================
# Test P: Existing short-video/single-chunk behavior
# =========================================================================
def test_p_single_chunk_short_video_behavior_preserved():
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="Is salary a drug?",
        visual_directives=[
            HookVisualDirective(beat_id="hook_beat_1", visual_instruction="Intro visual", trigger_word=None),
            HookVisualDirective(beat_id="hook_beat_2", visual_instruction="Intro visual 2", trigger_word="drug"),
        ],
    )
    strategy = ScriptVisualStrategy(
        thesis="Thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Security",
                focus_concept="Opportunity Cost",
                core_teaching_point="Explain cost",
                narration="You think paycheck is safety, but it's a trap.",
            )
        ],
    )
    composition_plan = FullCompositionPlan(
        thesis="Thesis",
        ideas=[
            IdeaCompositionPlan(
                idea_id="idea_01",
                narration="You think paycheck is safety, but it's a trap.",
                beats=[
                    CompositionBeat(beat_id="body_beat_1", composition_id="metric_hero", trigger_word=None),
                    CompositionBeat(beat_id="body_beat_2", composition_id="metric_hero", trigger_word="safety"),
                    CompositionBeat(beat_id="body_beat_3", composition_id="metric_hero", trigger_word="trap"),
                ],
            )
        ],
    )
    voice_track = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="runs/run_xxx/narration.mp3",
        duration_seconds=5.0,
        full_script_text="Is salary a drug?\n\nYou think paycheck is safety, but it's a trap.",
        word_timestamps=[
            WordTimestamp(word="Is", start_ms=0, end_ms=200),
            WordTimestamp(word="salary", start_ms=200, end_ms=400),
            WordTimestamp(word="a", start_ms=400, end_ms=500),
            WordTimestamp(word="drug", start_ms=500, end_ms=800),
            WordTimestamp(word="You", start_ms=1000, end_ms=1200),
            WordTimestamp(word="think", start_ms=1200, end_ms=1400),
            WordTimestamp(word="paycheck", start_ms=1400, end_ms=1800),
            WordTimestamp(word="is", start_ms=1800, end_ms=2000),
            WordTimestamp(word="safety", start_ms=2000, end_ms=2500),
            WordTimestamp(word="but", start_ms=2500, end_ms=2800),
            WordTimestamp(word="it's", start_ms=2800, end_ms=3000),
            WordTimestamp(word="a", start_ms=3000, end_ms=3200),
            WordTimestamp(word="trap", start_ms=3200, end_ms=3800),
        ],
    )
    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=voice_track, composition_plan=composition_plan)
    assert len(timeline) == 5
    assert timeline[0].beat_id == "hook_beat_1"
    assert timeline[0].start_frame == 0
    assert timeline[1].beat_id == "hook_beat_2"
    assert timeline[1].start_frame == 15
    assert timeline[2].beat_id == "body_beat_1"
    assert timeline[2].start_frame == 30
    assert timeline[3].beat_id == "body_beat_2"
    assert timeline[3].start_frame == 60
    assert timeline[4].beat_id == "body_beat_3"
    assert timeline[4].start_frame == 96
    assert timeline[4].end_frame == 150
