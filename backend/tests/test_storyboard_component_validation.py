"""Unit tests for storyboard component validation and semantic integrity checks."""
import pytest
from pydantic import ValidationError

from domain.storyboard import MacroScreenZone, MotionPreset, VisualActionType
from domain.storyboard_foundation import (
    StoryboardActionPlan,
    StoryboardBeatPlan,
    StoryboardStateChange,
    StoryboardVisualElement,
    WorldFoundationSpec,
)
from domain.validators.storyboard_semantic_validator import StoryboardSemanticValidator
from domain.visual_world import (
    LifecyclePolicy,
    StateChangeEvent,
    StateChangeKind,
    StoryboardBeat,
    VisualAction,
    VisualWorldSpec,
    WorldObjectSpec,
)


def _dummy_action(object_id: str, action_type: VisualActionType = VisualActionType.ENTER) -> StoryboardActionPlan:
    return StoryboardActionPlan(
        action_id=f"act_{object_id}",
        action_type=action_type,
        motion_preset=MotionPreset.REVEAL,
        order=1,
        trigger_word="salary",
        description=f"Action on {object_id}",
    )


# -----------------------------------------------------------------------------
# 1. StoryboardVisualElement Props Validation
# -----------------------------------------------------------------------------

def test_metric_card_props_validation_success():
    element = StoryboardVisualElement(
        object_id="card_1",
        component_type="MetricCard",
        macro_zone=MacroScreenZone.CENTER,
        semantic_content={
            "header": "TAX BRACKET",
            "display_value": "30%",
            "label": "HIGHEST SLAB",
            "tag": "OLD REGIME",
            "subtext": "Applies above 10L",
            "intent": "accent",
        },
        actions=[_dummy_action("card_1")],
    )
    assert element.component_type == "MetricCard"
    assert element.semantic_content["display_value"] == "30%"


def test_metric_card_props_validation_missing_required_fields():
    with pytest.raises(ValidationError) as exc_info:
        StoryboardVisualElement(
            object_id="card_1",
            component_type="MetricCard",
            semantic_content={
                "header": "TAX BRACKET",
                # missing display_value and label
            },
            actions=[_dummy_action("card_1")],
        )
    errors = str(exc_info.value)
    assert "display_value" in errors
    assert "label" in errors


def test_hero_stat_props_validation():
    # Valid
    element = StoryboardVisualElement(
        object_id="hero_1",
        component_type="HeroStat",
        macro_zone=MacroScreenZone.CENTER,
        semantic_content={
            "display_value": "₹45,000",
            "label": "MONTHLY TAKE-HOME",
            "badge_text": "BASE SALARY",
        },
        actions=[_dummy_action("hero_1")],
    )
    assert element.component_type == "HeroStat"

    # Missing label
    with pytest.raises(ValidationError):
        StoryboardVisualElement(
            object_id="hero_2",
            component_type="HeroStat",
            semantic_content={"display_value": "₹45,000"},
            actions=[_dummy_action("hero_2")],
        )


def test_comparison_card_props_validation():
    # Missing right side fields
    with pytest.raises(ValidationError):
        StoryboardVisualElement(
            object_id="comp_1",
            component_type="ComparisonCard",
            semantic_content={
                "title": "REGIME COMPARISON",
                "left_label": "OLD REGIME",
                "left_value": "₹3.5L",
                # missing right_label and right_value
            },
            actions=[_dummy_action("comp_1")],
        )

    # Valid
    element = StoryboardVisualElement(
        object_id="comp_1",
        component_type="ComparisonCard",
        macro_zone=MacroScreenZone.CENTER,
        semantic_content={
            "title": "REGIME COMPARISON",
            "left_label": "OLD REGIME",
            "left_value": "₹3.5L",
            "right_label": "NEW REGIME",
            "right_value": "₹2.8L",
        },
        actions=[_dummy_action("comp_1")],
    )
    assert element.component_type == "ComparisonCard"


def test_process_card_props_validation():
    # Less than 2 steps should fail
    with pytest.raises(ValidationError):
        StoryboardVisualElement(
            object_id="proc_1",
            component_type="ProcessCard",
            semantic_content={
                "title": "HOW IT WORKS",
                "steps": [{"step": 1, "title": "Single Step"}],
            },
            actions=[_dummy_action("proc_1")],
        )

    # Valid with 2 steps
    element = StoryboardVisualElement(
        object_id="proc_1",
        component_type="ProcessCard",
        macro_zone=MacroScreenZone.CENTER,
        semantic_content={
            "title": "HOW IT WORKS",
            "steps": [
                {"step": 1, "title": "Income Earned", "detail": "Gross Pay"},
                {"step": 2, "title": "TDS Deducted", "detail": "10% at Source"},
            ],
        },
        actions=[_dummy_action("proc_1")],
    )
    assert len(element.semantic_content["steps"]) == 2


def test_trend_line_chart_props_validation():
    # Fewer than 2 data points should fail
    with pytest.raises(ValidationError):
        StoryboardVisualElement(
            object_id="trend_1",
            component_type="TrendLineChart",
            semantic_content={
                "header": "SHORT TRAJECTORY",
                "data_points": [{"label": "2024", "value": 88.5}],
                "trend": "up",
            },
            actions=[_dummy_action("trend_1")],
        )

    # Valid TrendLineChart in StoryboardVisualElement
    element = StoryboardVisualElement(
        object_id="trend_1",
        component_type="TrendLineChart",
        macro_zone=MacroScreenZone.CENTER,
        semantic_content={
            "header": "USD / INR 5-YEAR TRAJECTORY",
            "data_points": [
                {"label": "2020", "value": 73.5},
                {"label": "2021", "value": 74.3},
                {"label": "2022", "value": 79.8},
                {"label": "2023", "value": 82.9},
                {"label": "2024", "value": 88.5},
            ],
            "trend": "down",
            "highlight_point": {"label": "2024 PEAK", "value": "₹88.50"},
        },
        actions=[_dummy_action("trend_1")],
    )
    assert element.component_type == "TrendLineChart"
    assert element.semantic_content["header"] == "USD / INR 5-YEAR TRAJECTORY"


def test_ranked_bar_chart_props_validation():
    # Fewer than 2 bars should fail
    with pytest.raises(ValidationError):
        StoryboardVisualElement(
            object_id="bar_1",
            component_type="RankedBarChart",
            semantic_content={
                "header": "SHORT RANKING",
                "bars": [{"label": "Single Bar", "value": 100}],
            },
            actions=[_dummy_action("bar_1")],
        )

    # Valid RankedBarChart in StoryboardVisualElement
    element = StoryboardVisualElement(
        object_id="bar_1",
        component_type="RankedBarChart",
        macro_zone=MacroScreenZone.CENTER,
        semantic_content={
            "title": "UPI MARKET SHARE BY APP",  # title alias maps to header
            "bars": [
                {"label": "PhonePe", "value": 48.6, "tag": "#1"},
                {"label": "Google Pay", "value": 36.2},
                {"label": "Paytm", "value": 8.1},
            ],
            "benchmark_value": 50.0,
            "benchmark_label": "50% Market Cap",
            "subtext": "Monthly transaction volume",
        },
        actions=[_dummy_action("bar_1")],
    )
    assert element.component_type == "RankedBarChart"
    assert element.semantic_content["header"] == "UPI MARKET SHARE BY APP"
    assert len(element.semantic_content["bars"]) == 3
    assert element.semantic_content["bars"][0]["display_value"] == "48.6"


def test_allocation_donut_props_validation():
    # Fewer than 2 slices should fail
    with pytest.raises(ValidationError):
        StoryboardVisualElement(
            object_id="donut_1",
            component_type="AllocationDonut",
            semantic_content={
                "header": "SHORT DONUT",
                "slices": [{"label": "Single Slice", "value": 100}],
            },
            actions=[_dummy_action("donut_1")],
        )

    # Valid AllocationDonut in StoryboardVisualElement with title alias
    element = StoryboardVisualElement(
        object_id="donut_1",
        component_type="AllocationDonut",
        macro_zone=MacroScreenZone.CENTER,
        semantic_content={
            "title": "AGGRESSIVE GROWTH ASSET MIX",  # title alias maps to header
            "slices": [
                {"label": "Equities", "value": 65.0, "tag": "Core"},
                {"label": "Debt", "value": 25.0},
                {"label": "Gold", "value": 10.0, "display_value": "10%"},
            ],
            "center_label": "TOTAL ALLOCATION",
            "center_value": "100%",
            "subtext": "Recommended high-equity blend",
        },
        actions=[_dummy_action("donut_1")],
    )
    assert element.component_type == "AllocationDonut"
    assert element.semantic_content["header"] == "AGGRESSIVE GROWTH ASSET MIX"
    assert len(element.semantic_content["slices"]) == 3
    assert element.semantic_content["slices"][1]["display_value"] == "25"
    assert element.semantic_content["center_value"] == "100%"


def test_waterfall_bridge_props_validation():
    # Fewer than 3 steps should fail
    with pytest.raises(ValidationError):
        StoryboardVisualElement(
            object_id="bridge_1",
            component_type="WaterfallBridge",
            semantic_content={
                "header": "SHORT BRIDGE",
                "steps": [
                    {"label": "Start", "value": 100},
                    {"label": "End", "value": 50},
                ],
            },
            actions=[_dummy_action("bridge_1")],
        )

    # Valid WaterfallBridge in StoryboardVisualElement with title alias
    element = StoryboardVisualElement(
        object_id="bridge_1",
        component_type="WaterfallBridge",
        macro_zone=MacroScreenZone.CENTER,
        semantic_content={
            "title": "PROFITABILITY WATERFALL",  # title alias maps to header
            "steps": [
                {"label": "Gross Revenue", "value": 100.0, "is_total": True},
                {"label": "COGS", "value": -40.0},
                {"label": "OpEx", "value": -25.0, "display_value": "-₹25 Cr"},
                {"label": "Net Profit", "value": 35.0, "is_total": True},
            ],
            "subtext": "Operational EBITDA bridge",
        },
        actions=[_dummy_action("bridge_1")],
    )
    assert element.component_type == "WaterfallBridge"
    assert element.semantic_content["header"] == "PROFITABILITY WATERFALL"
    assert len(element.semantic_content["steps"]) == 4
    assert element.semantic_content["steps"][1]["display_value"] == "-40"
    assert element.semantic_content["steps"][2]["display_value"] == "-₹25 Cr"




# -----------------------------------------------------------------------------
# 2. Beat Plan Requires at Least One Visual Element
# -----------------------------------------------------------------------------

def test_beat_plan_cannot_have_empty_elements():
    with pytest.raises(ValidationError):
        StoryboardBeatPlan(
            beat_id="beat_empty",
            narration="This beat tries to have no visual elements.",
            visual_goal="Explain nothing",
            visual_strategy="None",
            elements=[],  # must fail min_length=1
        )


# -----------------------------------------------------------------------------
# 3. StoryboardSemanticValidator Blocker Tests
# -----------------------------------------------------------------------------

def test_semantic_validator_blocks_beat_with_all_elements_hidden():
    validator = StoryboardSemanticValidator()

    # Beat where object is covered, but state_change_events sets it to hidden
    world = VisualWorldSpec(
        world_id="test_world",
        beats=[
            StoryboardBeat(
                beat_id="beat_01",
                narration="Here is your salary.",
                semantic_goal="Show salary",
                actions=[
                    VisualAction(
                        action_id="act_01",
                        target_node_id="card_1",
                        action_type=VisualActionType.ENTER,
                        trigger_word="salary",
                    )
                ],
                state_change_events=[
                    StateChangeEvent(
                        event_id="evt_hide",
                        beat_id="beat_01",
                        object_id="card_1",
                        kind=StateChangeKind.VISIBILITY,
                        visible=False,
                    )
                ],
            )
        ],
        objects=[
            WorldObjectSpec(
                object_id="card_1",
                component_type="MetricCard",
                semantic_content={
                    "header": "TAX",
                    "display_value": "30%",
                    "label": "SLAB",
                },
                beat_ids=["beat_01"],
            )
        ],
    )

    result = validator.validate(world)
    assert result.status == "blocked"
    assert any("hidden/invisible" in err for err in result.errors)


def test_semantic_validator_blocks_beat_with_no_actions():
    validator = StoryboardSemanticValidator()

    world = VisualWorldSpec(
        world_id="test_world",
        beats=[
            StoryboardBeat(
                beat_id="beat_01",
                narration="No actions happening here.",
                semantic_goal="Test no actions",
                actions=[],  # Empty actions
            )
        ],
        objects=[
            WorldObjectSpec(
                object_id="card_1",
                component_type="MetricCard",
                semantic_content={
                    "header": "TAX",
                    "display_value": "30%",
                    "label": "SLAB",
                },
                beat_ids=["beat_01"],
            )
        ],
    )

    result = validator.validate(world)
    assert result.status == "blocked"
    assert any("zero visual actions" in err for err in result.errors)


# -----------------------------------------------------------------------------
# 4. Simplified Foundation Contract & Python Defaults Tests
# -----------------------------------------------------------------------------

def test_minimal_element_auto_generates_enter_action_and_defaults():
    spec = WorldFoundationSpec(
        world_id="test_minimal_world",
        beats=[
            StoryboardBeatPlan(
                beat_id="beat_01",
                narration="When markets shift rapidly, prudent investors rebalance.",
                visual_goal="Highlight market shift",
                visual_strategy="Show hero stat",
                elements=[
                    StoryboardVisualElement(
                        object_id="shift_stat",
                        component_type="HeroStat",
                        semantic_content={
                            "label": "MARKET VOLATILITY",
                            "display_value": "24.5%",
                        },
                    ),
                    StoryboardVisualElement(
                        object_id="advice_callout",
                        component_type="Callout",
                        semantic_content={
                            "text": "Rebalancing secures locked-in gains.",
                        },
                    ),
                ],
            )
        ],
    )

    beat = spec.beats[0]
    # First element defaults to primary, center, beat_local
    el1 = beat.elements[0]
    assert el1.role == "primary"
    assert el1.macro_zone == MacroScreenZone.CENTER
    assert el1.lifecycle_mode == "beat_local"
    assert len(el1.actions) == 1
    assert el1.actions[0].action_type == VisualActionType.ENTER
    assert el1.actions[0].order == 1
    assert el1.actions[0].trigger_word == "when"

    # Second element defaults to supporting, center, beat_local
    el2 = beat.elements[1]
    assert el2.role == "supporting"
    assert el2.macro_zone == MacroScreenZone.CENTER
    assert el2.lifecycle_mode == "beat_local"
    assert len(el2.actions) == 1
    assert el2.actions[0].action_type == VisualActionType.ENTER
    assert el2.actions[0].order == 2


def test_reused_element_inherits_props_and_generates_hold_action():
    spec = WorldFoundationSpec(
        world_id="test_reuse_world",
        beats=[
            StoryboardBeatPlan(
                beat_id="beat_01",
                narration="When the repo rate jumps by fifty basis points.",
                visual_goal="Show rate hike",
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
                narration="Borrowers immediately absorb the increased monthly EMI.",
                visual_goal="Explain borrower absorption",
                visual_strategy="Retain rate stat and introduce callout",
                elements=[
                    # Reused element only specifies object_id
                    StoryboardVisualElement(
                        object_id="rate_stat",
                        macro_zone=MacroScreenZone.LEFT,
                    ),
                    StoryboardVisualElement(
                        object_id="emi_callout",
                        component_type="Callout",
                        semantic_content={
                            "text": "Floating EMIs expand automatically.",
                        },
                    ),
                ],
            ),
        ],
    )

    # Both appearances should be marked persistent
    el1_b1 = spec.beats[0].elements[0]
    el1_b2 = spec.beats[1].elements[0]
    assert el1_b1.lifecycle_mode == "persistent"
    assert el1_b2.lifecycle_mode == "persistent"

    # Reused element in beat 2 inherits component_type and semantic_content
    assert el1_b2.component_type == "HeroStat"
    assert el1_b2.semantic_content["display_value"] == "6.50%"
    assert el1_b2.macro_zone == MacroScreenZone.LEFT

    # Beat 2 automatically generated hold action for the reused element
    assert len(el1_b2.actions) == 1
    assert el1_b2.actions[0].action_type == VisualActionType.HOLD
    assert el1_b2.actions[0].trigger_word == "borrowers"


def test_unsupported_action_on_component_raises_error():
    with pytest.raises(ValueError) as exc_info:
        WorldFoundationSpec(
            world_id="test_invalid_action",
            beats=[
                StoryboardBeatPlan(
                    beat_id="beat_01",
                    narration="Follow these steps carefully.",
                    visual_goal="Test invalid action",
                    visual_strategy="Process card with update_value",
                    elements=[
                        StoryboardVisualElement(
                            object_id="proc_1",
                            component_type="ProcessCard",
                            semantic_content={
                                "steps": [
                                    {"title": "Step 1"},
                                    {"title": "Step 2"},
                                ]
                            },
                            actions=[
                                StoryboardActionPlan(
                                    action_type=VisualActionType.UPDATE_VALUE,
                                    target_property="value",
                                    new_value=2,
                                )
                            ],
                        )
                    ],
                )
            ],
        )
    err = str(exc_info.value)
    assert "Component 'ProcessCard' on 'proc_1' does not support action 'update_value'" in err


def test_action_trigger_word_must_appear_in_narration():
    with pytest.raises(ValueError) as exc_info:
        WorldFoundationSpec(
            world_id="test_missing_trigger",
            beats=[
                StoryboardBeatPlan(
                    beat_id="beat_01",
                    narration="When the benchmark interest rate climbs.",
                    visual_goal="Test missing trigger",
                    visual_strategy="Hero stat",
                    elements=[
                        StoryboardVisualElement(
                            object_id="stat_1",
                            component_type="HeroStat",
                            semantic_content={
                                "label": "RATE",
                                "display_value": "7%",
                            },
                            actions=[
                                StoryboardActionPlan(
                                    action_type=VisualActionType.ENTER,
                                    trigger_word="nonexistentword",
                                )
                            ],
                        )
                    ],
                )
            ],
        )
    assert "does not appear in the beat narration" in str(exc_info.value)


def test_chronological_trigger_order_violation_raises_error():
    with pytest.raises(ValueError) as exc_info:
        WorldFoundationSpec(
            world_id="test_chronology",
            beats=[
                StoryboardBeatPlan(
                    beat_id="beat_01",
                    narration="When rates climb slowly across time.",
                    visual_goal="Test trigger order",
                    visual_strategy="Hero stat",
                    elements=[
                        StoryboardVisualElement(
                            object_id="stat_1",
                            component_type="HeroStat",
                            semantic_content={
                                "label": "RATE",
                                "display_value": "7%",
                            },
                            actions=[
                                StoryboardActionPlan(
                                    action_type=VisualActionType.ENTER,
                                    order=1,
                                    trigger_word="slowly",  # word 3
                                ),
                                StoryboardActionPlan(
                                    action_type=VisualActionType.UPDATE_VALUE,
                                    order=2,
                                    trigger_word="when",  # word 0, earlier than slowly!
                                    target_property="value",
                                    new_value=8.0,
                                ),
                            ],
                        )
                    ],
                )
            ],
        )
    assert "Chronological trigger order violation" in str(exc_info.value)


def test_derived_chronological_action_ordering():
    spec = WorldFoundationSpec(
        world_id="test_derived_order",
        beats=[
            StoryboardBeatPlan(
                beat_id="beat_01",
                narration="When repo rates climb rapidly, inflation cools.",
                visual_goal="Show climb and cool",
                visual_strategy="Hero stat and callout",
                elements=[
                    StoryboardVisualElement(
                        object_id="stat_1",
                        component_type="HeroStat",
                        semantic_content={
                            "label": "RATE",
                            "display_value": "6.5%",
                        },
                        actions=[
                            # Order omitted -> derived by trigger_word
                            StoryboardActionPlan(
                                action_type=VisualActionType.ENTER,
                                trigger_word="when",  # word 0
                            ),
                            StoryboardActionPlan(
                                action_type=VisualActionType.UPDATE_VALUE,
                                trigger_word="climb",  # word 2
                                target_property="value",
                                new_value=7.0,
                            ),
                        ],
                    ),
                    StoryboardVisualElement(
                        object_id="callout_1",
                        component_type="Callout",
                        semantic_content={"text": "Cooling pressure"},
                        actions=[
                            StoryboardActionPlan(
                                action_type=VisualActionType.ENTER,
                                trigger_word="inflation",  # word 4
                            )
                        ],
                    ),
                ],
            )
        ],
    )

    beat = spec.beats[0]
    assert beat.elements[0].actions[0].order == 1
    assert beat.elements[0].actions[1].order == 2
    assert beat.elements[1].actions[0].order == 3


def test_assemble_visual_world_with_simplified_spec():
    from engines.scene_storyboarder_engine import SceneStoryboarderEngine

    spec = WorldFoundationSpec(
        world_id="test_assembly_world",
        beats=[
            StoryboardBeatPlan(
                beat_id="beat_01",
                narration="When the central bank hikes rates.",
                visual_goal="Show hike",
                visual_strategy="Center hero stat",
                elements=[
                    StoryboardVisualElement(
                        object_id="hike_stat",
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
                narration="Borrowers experience higher monthly charges.",
                visual_goal="Show charges",
                visual_strategy="Retain stat and show callout",
                elements=[
                    StoryboardVisualElement(object_id="hike_stat"),
                    StoryboardVisualElement(
                        object_id="charges_callout",
                        component_type="Callout",
                        semantic_content={"text": "Higher charges apply."},
                    ),
                ],
            ),
        ],
    )

    visual_world = SceneStoryboarderEngine.assemble_visual_world(spec)
    assert visual_world.world_id == "test_assembly_world"
    assert len(visual_world.beats) == 2
    assert len(visual_world.objects) == 2

    # hike_stat should be persistent and appear in both beats
    hike_obj = next(o for o in visual_world.objects if o.object_id == "hike_stat")
    assert hike_obj.lifecycle.mode == "persistent"
    assert hike_obj.beat_ids == ["beat_01", "beat_02"]

    # Beat 1 has 1 action (enter)
    assert len(visual_world.beats[0].actions) == 1
    assert visual_world.beats[0].actions[0].action_type == VisualActionType.ENTER

    # Beat 2 has 2 actions (hold for hike_stat, enter for charges_callout)
    assert len(visual_world.beats[1].actions) == 2
    act_types = [a.action_type for a in visual_world.beats[1].actions]
    assert VisualActionType.HOLD in act_types
    assert VisualActionType.ENTER in act_types


def test_metric_card_amount_stat_metric_alias_resolution():
    """Verify that MetricCardProps and StoryboardVisualElement rescue common aliases like amount, stat, metric."""
    from registries.visual_component_registry import VisualComponentRegistry

    # 1. 'amount' alias
    props1 = VisualComponentRegistry.validate_props("MetricCard", {
        "label": "TAKE-HOME",
        "amount": "₹4.6 LAKH",
    })
    assert props1.display_value == "₹4.6 LAKH"

    # 2. 'stat' alias
    props2 = VisualComponentRegistry.validate_props("MetricCard", {
        "label": "TAX RATE",
        "stat": "39%",
    })
    assert props2.display_value == "39%"

    # 3. 'metric' alias
    props3 = VisualComponentRegistry.validate_props("MetricCard", {
        "label": "SURCHARGE",
        "metric": 25.0,
    })
    assert props3.display_value == "25.0"
    assert props3.raw_value == 25.0


def test_storyboard_trigger_word_fuzzy_matching():
    """Verify that minor word variation/typo (e.g. 'break' -> 'breaks') auto-resolves silently."""
    spec = WorldFoundationSpec(
        world_id="test_fuzzy_world",
        beats=[
            StoryboardBeatPlan(
                beat_id="beat_01",
                narration="When the salary arrives, the math breaks down completely.",
                visual_goal="Show math breakdown",
                visual_strategy="Display stat",
                elements=[
                    StoryboardVisualElement(
                        object_id="breakdown_stat",
                        component_type="HeroStat",
                        semantic_content={"label": "NET LOSS", "display_value": "45%"},
                        actions=[
                            StoryboardActionPlan(
                                action_type=VisualActionType.ENTER,
                                trigger_word="break",  # Typo: 'break' instead of 'breaks'
                            )
                        ],
                    )
                ],
            )
        ],
    )
    assert spec.beats[0].elements[0].actions[0].trigger_word == "breaks"


def test_metric_card_and_herostat_label_as_display_value_auto_rescue():
    """Verify that when an LLM puts a formatted stat into 'label' instead of 'display_value', it is auto-rescued."""
    from registries.visual_component_registry import VisualComponentRegistry
    from engines.scene_storyboarder_engine import _sanitize_and_repair_foundation_payload

    # 1. MetricCard: 'header' + 'label' with percentage
    props1 = VisualComponentRegistry.validate_props("MetricCard", {
        "header": "AGGREGATOR TAKE RATE",
        "label": "18% to 25% take rate",
    })
    assert props1.display_value == "18% to 25% take rate"
    assert props1.label == "AGGREGATOR TAKE RATE"

    # 2. MetricCard: 'header' + 'label' with currency
    props2 = VisualComponentRegistry.validate_props("MetricCard", {
        "header": "RIDER PAYOUT",
        "label": "₹30 - ₹45 per delivery",
    })
    assert props2.display_value == "₹30 - ₹45 per delivery"
    assert props2.label == "RIDER PAYOUT"

    # 3. MetricCard: 'header' + 'label' with fee range
    props3 = VisualComponentRegistry.validate_props("MetricCard", {
        "header": "CONSUMER SURCHARGE",
        "label": "₹6 to ₹10 per order",
    })
    assert props3.display_value == "₹6 to ₹10 per order"
    assert props3.label == "CONSUMER SURCHARGE"

    # 4. MetricCard without digits should raise ValidationError (display_value required)
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        VisualComponentRegistry.validate_props("MetricCard", {
            "header": "CONSUMER SURCHARGE",
            "label": "CONSUMER SURCHARGE",
        })

    # 5. HeroStat: 'label' with number and 'subtext'
    props5 = VisualComponentRegistry.validate_props("HeroStat", {
        "label": "₹1 CRORE",
        "subtext": "HEADLINE CTC",
    })
    assert props5.display_value == "₹1 CRORE"
    assert props5.label == "HEADLINE CTC"

    # 6. Verify end-to-end via _sanitize_and_repair_foundation_payload
    raw_payload = {
        "world_id": "test_world",
        "beats": [
            {
                "beat_id": "beat_1",
                "narration": "The aggregator takes a steep cut from every order.",
                "elements": [
                    {
                        "object_id": "aggregator_commission",
                        "component_type": "MetricCard",
                        "semantic_content": {
                            "header": "AGGREGATOR TAKE RATE",
                            "label": "18% to 25% take rate",
                        },
                    }
                ],
            }
        ],
    }
    repaired = _sanitize_and_repair_foundation_payload(raw_payload)
    el_sem = repaired["beats"][0]["elements"][0]["semantic_content"]
    assert el_sem["display_value"] == "18% to 25% take rate"
    assert el_sem["label"] == "AGGREGATOR TAKE RATE"


