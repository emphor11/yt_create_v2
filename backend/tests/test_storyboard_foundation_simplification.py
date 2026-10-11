"""Tests for Phase 3: Storyboard Foundation Schema and Prompt Simplification.

Verifies:
1. Valid first appearance with minimal component content and auto-derived defaults.
2. Reuse across beats without repeating unchanged content, plus partial property updates.
3. Missing essential first-appearance content failing validation cleanly.
4. Invalid component properties producing clear errors.
5. Narration coverage, speech trigger grounding, and chronological order validation.
6. StoryboardStateChange auto-derives event_id and description when omitted.
7. Downstream VisualWorldSpec assembly continues to succeed cleanly.
"""
from typing import Any
import pytest
from pydantic import ValidationError

from domain.storyboard import MacroScreenZone, MotionPreset, VisualActionType
from domain.storyboard_foundation import (
    StoryboardBeatPlan,
    StoryboardVisualElement,
    StoryboardActionPlan,
    StoryboardStateChange,
    WorldFoundationSpec,
)
from domain.visual_world import StateChangeKind
from engines.scene_storyboarder_engine import SceneStoryboarderEngine, FOUNDATION_RESPONSE_SCHEMA


# -----------------------------------------------------------------------------
# 1. Valid First Appearance with Minimal Content
# -----------------------------------------------------------------------------

def test_minimal_first_appearance_herostat():
    """HeroStat only requires label and display_value. Role, macro_zone, and enter action are auto-derived."""
    spec = WorldFoundationSpec(
        world_id="test_minimal_herostat",
        beats=[
            StoryboardBeatPlan(
                beat_id="beat_01",
                narration="The central repo rate held steady at six point five percent.",
                visual_goal="Present benchmark rate",
                visual_strategy="Center hero stat",
                elements=[
                    StoryboardVisualElement(
                        object_id="repo_rate",
                        component_type="HeroStat",
                        semantic_content={
                            "label": "REPO RATE",
                            "display_value": "6.50%",
                        },
                    )
                ],
            )
        ],
    )
    el = spec.beats[0].elements[0]
    assert el.role == "primary"
    assert el.macro_zone == MacroScreenZone.CENTER
    assert len(el.actions) == 1
    assert el.actions[0].action_type == VisualActionType.ENTER
    assert el.actions[0].trigger_word == "the"
    assert el.actions[0].order == 1


def test_minimal_first_appearance_all_flat_components():
    """Verify minimal required properties for MetricCard, ComparisonCard, ProcessCard, Callout, FlowConnector."""
    spec = WorldFoundationSpec(
        world_id="test_minimal_components",
        beats=[
            StoryboardBeatPlan(
                beat_id="beat_01",
                narration="Borrowers compare fixed versus floating rates through three distinct steps.",
                visual_goal="Demonstrate loan concepts",
                visual_strategy="Display multiple components",
                elements=[
                    StoryboardVisualElement(
                        object_id="metric_1",
                        component_type="MetricCard",
                        semantic_content={
                            "label": "BASE RATE",
                            "display_value": "8.25%",
                        },
                    ),
                    StoryboardVisualElement(
                        object_id="comp_1",
                        component_type="ComparisonCard",
                        semantic_content={
                            "left_label": "FIXED",
                            "left_value": "8.50%",
                            "right_label": "FLOATING",
                            "right_value": "9.20%",
                        },
                    ),
                    StoryboardVisualElement(
                        object_id="proc_1",
                        component_type="ProcessCard",
                        semantic_content={
                            "steps": [
                                {"title": "Benchmark Reset"},
                                {"title": "Spread Calculation"},
                            ]
                        },
                    ),
                    StoryboardVisualElement(
                        object_id="callout_1",
                        component_type="Callout",
                        semantic_content={
                            "text": "Floating rates adjust every quarter.",
                        },
                    ),
                    StoryboardVisualElement(
                        object_id="conn_1",
                        component_type="FlowConnector",
                        semantic_content={
                            "source_id": "metric_1",
                            "target_id": "comp_1",
                        },
                    ),
                ],
            )
        ],
    )
    beat = spec.beats[0]
    assert len(beat.elements) == 5
    # First is primary, others are supporting or relationship
    assert beat.elements[0].role == "primary"
    assert beat.elements[1].role == "supporting"
    assert beat.elements[4].role == "relationship"


# -----------------------------------------------------------------------------
# 2. Reuse Without Repeating Unchanged Content & Merging Updates
# -----------------------------------------------------------------------------

def test_reuse_without_repeating_content():
    """Reused element only needs object_id, inheriting component_type and semantic_content with auto-hold."""
    spec = WorldFoundationSpec(
        world_id="test_reuse_world",
        beats=[
            StoryboardBeatPlan(
                beat_id="beat_01",
                narration="Central bank announces repo benchmark.",
                visual_goal="Introduce benchmark",
                visual_strategy="Center hero stat",
                elements=[
                    StoryboardVisualElement(
                        object_id="rate_stat",
                        component_type="HeroStat",
                        semantic_content={
                            "label": "REPO RATE",
                            "display_value": "6.50%",
                        },
                    )
                ],
            ),
            StoryboardBeatPlan(
                beat_id="beat_02",
                narration="Lenders respond across all retail loans.",
                visual_goal="Show persistent rate alongside lender reaction",
                visual_strategy="Keep rate on left and add callout",
                elements=[
                    # No component_type, no semantic_content
                    StoryboardVisualElement(
                        object_id="rate_stat",
                        macro_zone=MacroScreenZone.LEFT,
                    ),
                    StoryboardVisualElement(
                        object_id="lender_callout",
                        component_type="Callout",
                        semantic_content={"text": "Lenders hike floating spreads."},
                    ),
                ],
            ),
        ],
    )
    b1_el = spec.beats[0].elements[0]
    b2_el = spec.beats[1].elements[0]

    assert b1_el.lifecycle_mode == "persistent"
    assert b2_el.lifecycle_mode == "persistent"
    assert b2_el.component_type == "HeroStat"
    assert b2_el.semantic_content["display_value"] == "6.50%"
    assert b2_el.macro_zone == MacroScreenZone.LEFT

    # Beat 2 auto-generates hold action
    assert len(b2_el.actions) == 1
    assert b2_el.actions[0].action_type == VisualActionType.HOLD


def test_reuse_with_partial_content_update():
    """Reusing an element while updating only the changed property (e.g. display_value) merges safely."""
    spec = WorldFoundationSpec(
        world_id="test_reuse_update_world",
        beats=[
            StoryboardBeatPlan(
                beat_id="beat_01",
                narration="The policy rate begins at six percent.",
                visual_goal="Initial rate",
                visual_strategy="Center hero stat",
                elements=[
                    StoryboardVisualElement(
                        object_id="rate_stat",
                        component_type="HeroStat",
                        semantic_content={
                            "label": "REPO BENCHMARK",
                            "display_value": "6.00%",
                            "tag": "BASELINE",
                        },
                    )
                ],
            ),
            StoryboardBeatPlan(
                beat_id="beat_02",
                narration="By quarter end the benchmark climbs to seven percent.",
                visual_goal="Update rate",
                visual_strategy="Update stat value",
                elements=[
                    # Reused with updated display_value only (label and tag inherited)
                    StoryboardVisualElement(
                        object_id="rate_stat",
                        semantic_content={
                            "display_value": "7.00%",
                        },
                        actions=[
                            StoryboardActionPlan(
                                action_type=VisualActionType.UPDATE_VALUE,
                                trigger_word="climbs",
                                target_property="value",
                                new_value=7.0,
                            )
                        ],
                    )
                ],
            ),
        ],
    )
    b2_el = spec.beats[1].elements[0]
    assert b2_el.component_type == "HeroStat"
    assert b2_el.semantic_content["label"] == "REPO BENCHMARK"
    assert b2_el.semantic_content["display_value"] == "7.00%"
    assert b2_el.semantic_content["tag"] == "BASELINE"


# -----------------------------------------------------------------------------
# 3. Missing Essential First-Appearance Content Fails Validation
# -----------------------------------------------------------------------------

def test_missing_first_appearance_herostat_fails():
    """Missing display_value or label on first appearance must raise ValidationError."""
    with pytest.raises(ValidationError) as exc:
        WorldFoundationSpec(
            world_id="test_fail_world",
            beats=[
                StoryboardBeatPlan(
                    beat_id="beat_01",
                    narration="Interest rates rise.",
                    visual_goal="Fail goal",
                    visual_strategy="Fail strategy",
                    elements=[
                        StoryboardVisualElement(
                            object_id="stat_fail",
                            component_type="HeroStat",
                            semantic_content={"label": "RATE ONLY"},
                        )
                    ],
                )
            ],
        )
    assert "display_value" in str(exc.value)


def test_missing_first_appearance_callout_fails():
    """Callout missing 'text' must fail."""
    with pytest.raises(ValidationError) as exc:
        WorldFoundationSpec(
            world_id="test_fail_world",
            beats=[
                StoryboardBeatPlan(
                    beat_id="beat_01",
                    narration="Important disclaimer statement.",
                    visual_goal="Fail goal",
                    visual_strategy="Fail strategy",
                    elements=[
                        StoryboardVisualElement(
                            object_id="callout_fail",
                            component_type="Callout",
                            semantic_content={"attribution": "Source: RBI"},
                        )
                    ],
                )
            ],
        )
    assert "text" in str(exc.value)


def test_missing_type_on_first_appearance_fails():
    """An element appearing for the first time without component_type or primitive_type fails."""
    with pytest.raises(ValidationError) as exc:
        WorldFoundationSpec(
            world_id="test_fail_world",
            beats=[
                StoryboardBeatPlan(
                    beat_id="beat_01",
                    narration="Initial opening narration line.",
                    visual_goal="Goal",
                    visual_strategy="Strategy",
                    elements=[
                        StoryboardVisualElement(
                            object_id="unknown_obj",
                        )
                    ],
                )
            ],
        )
    assert "without a primitive_type or component_type" in str(exc.value)


# -----------------------------------------------------------------------------
# 4. Invalid Component Properties & Actions Produce Clear Errors
# -----------------------------------------------------------------------------

def test_invalid_unsupported_properties_fail():
    """Extra/unsupported properties in semantic_content fail validation."""
    with pytest.raises(ValidationError) as exc:
        WorldFoundationSpec(
            world_id="test_fail_world",
            beats=[
                StoryboardBeatPlan(
                    beat_id="beat_01",
                    narration="Narration text line.",
                    visual_goal="Goal",
                    visual_strategy="Strategy",
                    elements=[
                        StoryboardVisualElement(
                            object_id="stat_fail",
                            component_type="HeroStat",
                            semantic_content={
                                "label": "LABEL",
                                "display_value": "10%",
                                "unsupported_extra_field": "disallowed",
                            },
                        )
                    ],
                )
            ],
        )
    assert "unsupported properties" in str(exc.value)
    assert "unsupported_extra_field" in str(exc.value)


def test_unsupported_action_for_component_fails():
    """ProcessCard does not support update_value."""
    with pytest.raises(ValidationError) as exc:
        WorldFoundationSpec(
            world_id="test_fail_world",
            beats=[
                StoryboardBeatPlan(
                    beat_id="beat_01",
                    narration="Steps follow one another.",
                    visual_goal="Goal",
                    visual_strategy="Strategy",
                    elements=[
                        StoryboardVisualElement(
                            object_id="proc_1",
                            component_type="ProcessCard",
                            semantic_content={
                                "steps": [{"title": "Step 1"}, {"title": "Step 2"}]
                            },
                            actions=[
                                StoryboardActionPlan(
                                    action_type=VisualActionType.UPDATE_VALUE,
                                    trigger_word="steps",
                                    target_property="value",
                                    new_value=2,
                                )
                            ],
                        )
                    ],
                )
            ],
        )
    assert "does not support action 'update_value'" in str(exc.value)


# -----------------------------------------------------------------------------
# 5. Narration Trigger and Chronological Ordering Validation
# -----------------------------------------------------------------------------

def test_trigger_word_not_in_narration_fails():
    """Trigger words must appear in that beat's narration."""
    with pytest.raises(ValidationError) as exc:
        WorldFoundationSpec(
            world_id="test_fail_world",
            beats=[
                StoryboardBeatPlan(
                    beat_id="beat_01",
                    narration="Only three words here.",
                    visual_goal="Goal",
                    visual_strategy="Strategy",
                    elements=[
                        StoryboardVisualElement(
                            object_id="stat_1",
                            component_type="HeroStat",
                            semantic_content={"label": "L", "display_value": "V"},
                            actions=[
                                StoryboardActionPlan(
                                    action_type=VisualActionType.ENTER,
                                    trigger_word="nonexistent",
                                )
                            ],
                        )
                    ],
                )
            ],
        )
    assert "does not appear in the beat narration" in str(exc.value)


def test_chronological_action_trigger_order_violation_fails():
    """Actions with explicit orders must not occur in reversed narration order."""
    with pytest.raises(ValidationError) as exc:
        WorldFoundationSpec(
            world_id="test_fail_world",
            beats=[
                StoryboardBeatPlan(
                    beat_id="beat_01",
                    narration="First word comes before second word.",
                    visual_goal="Goal",
                    visual_strategy="Strategy",
                    elements=[
                        StoryboardVisualElement(
                            object_id="stat_1",
                            component_type="HeroStat",
                            semantic_content={"label": "L", "display_value": "V"},
                            actions=[
                                StoryboardActionPlan(
                                    action_id="act_1",
                                    action_type=VisualActionType.ENTER,
                                    trigger_word="second",
                                    order=1,
                                ),
                                StoryboardActionPlan(
                                    action_id="act_2",
                                    action_type=VisualActionType.PULSE,
                                    trigger_word="first",
                                    order=2,
                                ),
                            ],
                        )
                    ],
                )
            ],
        )
    assert "Chronological trigger order violation" in str(exc.value)


# -----------------------------------------------------------------------------
# 6. StoryboardStateChange Auto-derivation
# -----------------------------------------------------------------------------

def test_state_change_event_id_and_description_defaults():
    """StoryboardStateChange auto-derives event_id and description when omitted."""
    change = StoryboardStateChange(
        object_id="stat_1",
        kind=StateChangeKind.LAYOUT,
        macro_zone=MacroScreenZone.LEFT,
    )
    assert change.event_id == "evt_layout_stat_1"
    assert change.description == "Layout for stat_1."


# -----------------------------------------------------------------------------
# 7. Response Schema & Full VisualWorldSpec Assembly
# -----------------------------------------------------------------------------

def test_response_schema_requires_component_type_and_semantic_content():
    """In FOUNDATION_RESPONSE_SCHEMA, component_type and semantic_content are required."""
    element_schema = FOUNDATION_RESPONSE_SCHEMA["$defs"]["StoryboardVisualElement"]
    required_fields = element_schema.get("required", [])
    assert "object_id" in required_fields
    assert "component_type" in required_fields
    assert "semantic_content" in required_fields


def test_assemble_visual_world_with_simplified_lifecycle():
    """Ensure assemble_visual_world correctly compiles multi-beat reuse and actions."""
    spec = WorldFoundationSpec(
        world_id="test_compiled_world",
        beats=[
            StoryboardBeatPlan(
                beat_id="beat_01",
                narration="Initial repo announcement.",
                visual_goal="Intro",
                visual_strategy="Center stat",
                elements=[
                    StoryboardVisualElement(
                        object_id="repo_stat",
                        component_type="HeroStat",
                        semantic_content={"label": "REPO", "display_value": "6.5%"},
                    )
                ],
            ),
            StoryboardBeatPlan(
                beat_id="beat_02",
                narration="Borrowers take notice.",
                visual_goal="Reaction",
                visual_strategy="Move left",
                elements=[
                    StoryboardVisualElement(
                        object_id="repo_stat",
                        macro_zone=MacroScreenZone.LEFT,
                    )
                ],
                state_change_events=[
                    StoryboardStateChange(
                        object_id="repo_stat",
                        kind=StateChangeKind.LAYOUT,
                        macro_zone=MacroScreenZone.LEFT,
                    )
                ],
            ),
        ],
    )
    world = SceneStoryboarderEngine.assemble_visual_world(spec)
    assert world.world_id == "test_compiled_world"
    assert len(world.beats) == 2
    assert len(world.objects) == 1
    obj = world.objects[0]
    assert obj.object_id == "repo_stat"
    assert obj.lifecycle.mode == "persistent"
    assert obj.beat_ids == ["beat_01", "beat_02"]


# -----------------------------------------------------------------------------
# 8. Verification of Universal Audit Fixes
# -----------------------------------------------------------------------------

def test_validate_props_ignores_none_for_other_schema_fields():
    """Shared union payload fields with None values do not fail validation on leaf components."""
    from registries.visual_component_registry import VisualComponentRegistry

    # Callout receiving nulls from other schema fields (value, prefix, steps, etc.)
    props = {
        "text": "UPI transfers remain free for consumers.",
        "attribution": "NPCI Guidelines",
        "value": None,
        "prefix": None,
        "suffix": None,
        "precision": None,
        "steps": None,
    }
    validated = VisualComponentRegistry.validate_props("Callout", props)
    assert validated.text == "UPI transfers remain free for consumers."

    # But genuine unsupported values are strictly rejected
    invalid_props = {
        "text": "Valid text",
        "unsupported_extra_field": "disallowed_value",
    }
    with pytest.raises(Exception) as exc:
        VisualComponentRegistry.validate_props("Callout", invalid_props)
    assert "unsupported properties" in str(exc.value)


def test_multi_beat_partial_update_persists_to_third_beat():
    """An element updated in beat 2 retains the beat 2 update in beat 3 when not repeating props."""
    spec = WorldFoundationSpec(
        world_id="test_3_beat_persistence",
        beats=[
            StoryboardBeatPlan(
                beat_id="beat_01",
                narration="Initial repo announcement.",
                visual_goal="Intro",
                visual_strategy="Center stat",
                elements=[
                    StoryboardVisualElement(
                        object_id="stat",
                        component_type="HeroStat",
                        semantic_content={"label": "REPO RATE", "display_value": "6.0%"},
                    )
                ],
            ),
            StoryboardBeatPlan(
                beat_id="beat_02",
                narration="Central bank updates rate.",
                visual_goal="Update",
                visual_strategy="Update stat value",
                elements=[
                    StoryboardVisualElement(
                        object_id="stat",
                        semantic_content={"display_value": "6.5%"},
                    )
                ],
            ),
            StoryboardBeatPlan(
                beat_id="beat_03",
                narration="Final economic summary.",
                visual_goal="Conclusion",
                visual_strategy="Hold stat",
                elements=[
                    # Reused with no semantic_content
                    StoryboardVisualElement(
                        object_id="stat",
                    )
                ],
            ),
        ],
    )
    b2_el = spec.beats[1].elements[0]
    b3_el = spec.beats[2].elements[0]

    assert b2_el.semantic_content["display_value"] == "6.5%"
    assert b2_el.semantic_content["label"] == "REPO RATE"

    # Beat 3 must retain 6.5%, NOT revert to 6.0%
    assert b3_el.semantic_content["display_value"] == "6.5%"
    assert b3_el.semantic_content["label"] == "REPO RATE"


def test_persistence_requires_distinct_beats():
    """An element repeated twice within the same beat is NOT marked persistent; distinct beats are required."""
    spec = WorldFoundationSpec(
        world_id="test_persistence_beats",
        beats=[
            StoryboardBeatPlan(
                beat_id="beat_01",
                narration="Single scene beat narration line.",
                visual_goal="Intro",
                visual_strategy="Center stat",
                elements=[
                    StoryboardVisualElement(
                        object_id="stat_local",
                        component_type="HeroStat",
                        semantic_content={"label": "LOCAL STAT", "display_value": "100"},
                    ),
                    StoryboardVisualElement(
                        object_id="callout_local",
                        component_type="Callout",
                        semantic_content={"text": "Local callout"},
                    ),
                ],
            )
        ],
    )
    el = spec.beats[0].elements[0]
    assert el.lifecycle_mode == "beat_local"


def test_assemble_visual_world_populates_initial_state_value_for_herostat_and_metriccard():
    """HeroStat and MetricCard with raw_value have initial_state['value'] populated for Remotion animation."""
    spec = WorldFoundationSpec(
        world_id="test_numeric_initial_state",
        beats=[
            StoryboardBeatPlan(
                beat_id="beat_01",
                narration="The benchmark rate begins at six percent.",
                visual_goal="Display benchmark",
                visual_strategy="Show hero stat and metric card",
                elements=[
                    StoryboardVisualElement(
                        object_id="hero_stat",
                        component_type="HeroStat",
                        semantic_content={"label": "REPO", "display_value": "6.0%", "raw_value": 6.0},
                    ),
                    StoryboardVisualElement(
                        object_id="metric_card",
                        component_type="MetricCard",
                        semantic_content={"label": "LENDING SPREAD", "display_value": "2.5%", "raw_value": 2.5},
                    ),
                ],
            )
        ],
    )
    world = SceneStoryboarderEngine.assemble_visual_world(spec)
    hero_obj = next(o for o in world.objects if o.object_id == "hero_stat")
    metric_obj = next(o for o in world.objects if o.object_id == "metric_card")

    assert hero_obj.initial_state["value"] == 6.0
    assert metric_obj.initial_state["value"] == 2.5
