"""Focused unit and integration tests for the Scene Storyboarder contract.

Tests verify:
1. Centered vertical metric composition
2. Left/right split composition
3. Persistent object across scenes
4. Multiple actions within one scene
5. Nested primitive groups
6. Trigger-word validation (matching, punctuation, missing words, multiple occurrences)
7. Rejection of downstream geometry, frames, and timestamps
8. Rejection of high-level composition/template names
"""
import pytest
from pydantic import ValidationError

from domain.storyboard import (
    SceneStoryboardSpec,
    ProjectStoryboardSpec,
    StoryboardNode,
    VisualAction,
    VisualActionType,
    MotionPreset,
    MacroScreenZone,
    ContainerFlow,
    FlowAlignment,
    FlowJustification,
    SemanticSpacing,
    MicroLayoutFlow,
    SemanticColorRole,
    SemanticTypographyRole,
    SemanticRadiusRole,
    SemanticElevationRole,
    SemanticStyleIntent,
)
from domain.primitives.common import CanonicalCapabilityType
from domain.validators.storyboard_validator import StoryboardValidator
from domain.visual_intent import VisualIntent, QuantitativeMeasurement, SemanticEntity


# -----------------------------------------------------------------------------
# 1. Centered Vertical Metric Composition
# -----------------------------------------------------------------------------
def test_centered_vertical_metric_composition() -> None:
    """Tests constructing a centered vertical metric card purely from primitives."""
    scene = SceneStoryboardSpec(
        scene_id="scene_01",
        narration="The starting monthly salary for this role is fifty thousand rupees.",
        macro_zone=MacroScreenZone.CENTER,
        root_nodes=[
            StoryboardNode(
                id="salary_metric_card",
                type=CanonicalCapabilityType.GROUP,
                macro_zone=MacroScreenZone.CENTER,
                flow=MicroLayoutFlow(
                    flow=ContainerFlow.COLUMN,
                    alignment=FlowAlignment.CENTER,
                    justification=FlowJustification.CENTER,
                    gap=SemanticSpacing.MD,
                    padding=SemanticSpacing.LG,
                ),
                style=SemanticStyleIntent(
                    fill_role=SemanticColorRole.SURFACE,
                    stroke_role=SemanticColorRole.BORDER,
                    radius_role=SemanticRadiusRole.CARD,
                    elevation_role=SemanticElevationRole.CARD,
                ),
                children=[
                    StoryboardNode(
                        id="salary_icon",
                        type=CanonicalCapabilityType.ICON,
                        style=SemanticStyleIntent(text_color_role=SemanticColorRole.ACCENT),
                        props={"icon_name": "briefcase", "size": 32},
                    ),
                    StoryboardNode(
                        id="salary_label",
                        type=CanonicalCapabilityType.TEXT,
                        style=SemanticStyleIntent(
                            typography_role=SemanticTypographyRole.CAPTION,
                            text_color_role=SemanticColorRole.SECONDARY_TEXT,
                        ),
                        props={"content": "Gross Monthly Salary"},
                    ),
                    StoryboardNode(
                        id="salary_number",
                        type=CanonicalCapabilityType.NUMBER,
                        style=SemanticStyleIntent(
                            typography_role=SemanticTypographyRole.DISPLAY,
                            text_color_role=SemanticColorRole.PRIMARY_TEXT,
                        ),
                        props={
                            "value": 50000,
                            "currency_symbol": "₹",
                            "format": "currency",
                        },
                    ),
                ],
            )
        ],
        actions=[
            VisualAction(
                action_id="act_reveal_salary",
                target_node_id="salary_number",
                action_type=VisualActionType.ENTER,
                trigger_word="salary",
                motion_preset=MotionPreset.IMPACT,
                description="Pop the number ticker into view when the speaker says 'salary'",
            )
        ],
    )

    validator = StoryboardValidator()
    result = validator.validate(scene)
    assert result.status == "valid", f"Expected valid, got errors: {result.errors}"
    assert len(scene.root_nodes[0].children) == 3


# -----------------------------------------------------------------------------
# 2. Left / Right Split Composition
# -----------------------------------------------------------------------------
def test_left_right_split_composition() -> None:
    """Tests side-by-side comparison assembled from two groups and a connector."""
    scene = SceneStoryboardSpec(
        scene_id="scene_02",
        narration="While your active income is capped, fixed rent consumes twenty thousand rupees immediately.",
        macro_zone=MacroScreenZone.CENTER,
        root_nodes=[
            # Left side
            StoryboardNode(
                id="income_card",
                type=CanonicalCapabilityType.GROUP,
                macro_zone=MacroScreenZone.SPLIT_LEFT,
                flow=MicroLayoutFlow(flow=ContainerFlow.COLUMN, gap=SemanticSpacing.SM),
                style=SemanticStyleIntent(fill_role=SemanticColorRole.SURFACE),
                children=[
                    StoryboardNode(
                        id="income_title",
                        type=CanonicalCapabilityType.TEXT,
                        style=SemanticStyleIntent(typography_role=SemanticTypographyRole.CAPTION),
                        props={"content": "Active Income"},
                    ),
                    StoryboardNode(
                        id="income_val",
                        type=CanonicalCapabilityType.NUMBER,
                        style=SemanticStyleIntent(
                            typography_role=SemanticTypographyRole.SUBHEADLINE,
                            text_color_role=SemanticColorRole.SUCCESS,
                        ),
                        props={"value": 50000, "currency_symbol": "₹", "format": "currency"},
                    ),
                ],
            ),
            # Right side
            StoryboardNode(
                id="rent_card",
                type=CanonicalCapabilityType.GROUP,
                macro_zone=MacroScreenZone.SPLIT_RIGHT,
                flow=MicroLayoutFlow(flow=ContainerFlow.COLUMN, gap=SemanticSpacing.SM),
                style=SemanticStyleIntent(fill_role=SemanticColorRole.SURFACE_ELEVATED),
                children=[
                    StoryboardNode(
                        id="rent_title",
                        type=CanonicalCapabilityType.TEXT,
                        style=SemanticStyleIntent(typography_role=SemanticTypographyRole.CAPTION),
                        props={"content": "Metro Rent"},
                    ),
                    StoryboardNode(
                        id="rent_val",
                        type=CanonicalCapabilityType.NUMBER,
                        style=SemanticStyleIntent(
                            typography_role=SemanticTypographyRole.SUBHEADLINE,
                            text_color_role=SemanticColorRole.DANGER,
                        ),
                        props={"value": 20000, "currency_symbol": "₹", "format": "currency"},
                    ),
                ],
            ),
            # Relational connector
            StoryboardNode(
                id="comparison_arrow",
                type=CanonicalCapabilityType.CONNECTOR,
                style=SemanticStyleIntent(stroke_role=SemanticColorRole.WARNING),
                props={
                    "from_node_id": "income_card",
                    "to_node_id": "rent_card",
                    "style": "straight",
                    "label": "40% Outflow",
                },
            ),
        ],
        actions=[
            VisualAction(
                action_id="act_income",
                target_node_id="income_card",
                action_type=VisualActionType.APPEAR,
                trigger_word="active",
            ),
            VisualAction(
                action_id="act_rent",
                target_node_id="rent_card",
                action_type=VisualActionType.APPEAR,
                trigger_word="rent",
            ),
            VisualAction(
                action_id="act_arrow",
                target_node_id="comparison_arrow",
                action_type=VisualActionType.ENTER,
                trigger_word="consumes",
                motion_preset=MotionPreset.REVEAL,
            ),
        ],
    )

    validator = StoryboardValidator()
    result = validator.validate(scene)
    assert result.status == "valid", f"Expected valid, got errors: {result.errors}"


# -----------------------------------------------------------------------------
# 3. Persistent Object Across Scenes
# -----------------------------------------------------------------------------
def test_persistent_object_across_scenes() -> None:
    """Tests an object carrying continuous identity across multiple scenes."""
    scene_1 = SceneStoryboardSpec(
        scene_id="scene_01",
        narration="You begin with a baseline investment of one lakh rupees.",
        root_nodes=[
            StoryboardNode(
                id="portfolio_s1",
                type=CanonicalCapabilityType.GROUP,
                persistence_key="user_portfolio",
                persistence_scope="cross_scene",
                macro_zone=MacroScreenZone.CENTER,
                flow=MicroLayoutFlow(flow=ContainerFlow.COLUMN),
                children=[
                    StoryboardNode(
                        id="portfolio_num_s1",
                        type=CanonicalCapabilityType.NUMBER,
                        props={"value": 100000, "currency_symbol": "₹", "format": "currency"},
                    )
                ],
            )
        ],
        actions=[
            VisualAction(
                action_id="act_s1",
                target_node_id="portfolio_s1",
                action_type=VisualActionType.ENTER,
                trigger_word="investment",
            )
        ],
    )

    scene_2 = SceneStoryboardSpec(
        scene_id="scene_02",
        narration="Compounding turns that investment into ten lakh over fifteen years.",
        root_nodes=[
            StoryboardNode(
                id="portfolio_s2",
                type=CanonicalCapabilityType.GROUP,
                persistence_key="user_portfolio",
                persistence_scope="cross_scene",
                macro_zone=MacroScreenZone.CENTER,
                flow=MicroLayoutFlow(flow=ContainerFlow.COLUMN),
                children=[
                    StoryboardNode(
                        id="portfolio_num_s2",
                        type=CanonicalCapabilityType.NUMBER,
                        props={"value": 1000000, "currency_symbol": "₹", "format": "currency"},
                    )
                ],
            )
        ],
        actions=[
            VisualAction(
                action_id="act_s2",
                target_node_id="portfolio_s2",
                action_type=VisualActionType.TRANSFORM,
                trigger_word="compounding",
                motion_preset=MotionPreset.SETTLE,
            )
        ],
    )

    project = ProjectStoryboardSpec(scenes=[scene_1, scene_2])
    validator = StoryboardValidator()
    result = validator.validate(project)
    assert result.status == "valid", f"Expected valid, got errors: {result.errors}"


# -----------------------------------------------------------------------------
# 4. Multiple Actions Within One Scene
# -----------------------------------------------------------------------------
def test_multiple_actions_within_one_scene() -> None:
    """Tests multiple spoken trigger words driving distinct sequential actions."""
    scene = SceneStoryboardSpec(
        scene_id="scene_03",
        narration="First note the target. Then subtract tax. Finally verify the net result.",
        root_nodes=[
            StoryboardNode(
                id="target_node",
                type=CanonicalCapabilityType.TEXT,
                props={"content": "Target: ₹100,000"},
            ),
            StoryboardNode(
                id="tax_node",
                type=CanonicalCapabilityType.NUMBER,
                props={"value": 30000, "currency_symbol": "₹", "format": "currency"},
            ),
            StoryboardNode(
                id="net_node",
                type=CanonicalCapabilityType.TEXT,
                props={"content": "Net: ₹70,000"},
            ),
        ],
        actions=[
            VisualAction(
                action_id="act_target",
                target_node_id="target_node",
                action_type=VisualActionType.APPEAR,
                trigger_word="target",
            ),
            VisualAction(
                action_id="act_tax",
                target_node_id="tax_node",
                action_type=VisualActionType.HIGHLIGHT,
                trigger_word="subtract",
                motion_preset=MotionPreset.IMPACT,
            ),
            VisualAction(
                action_id="act_net",
                target_node_id="net_node",
                action_type=VisualActionType.ENTER,
                trigger_word="verify",
                motion_preset=MotionPreset.SETTLE,
            ),
        ],
    )

    validator = StoryboardValidator()
    result = validator.validate(scene)
    assert result.status == "valid", f"Expected valid, got errors: {result.errors}"
    assert len(scene.actions) == 3


# -----------------------------------------------------------------------------
# 5. Nested Primitive Groups
# -----------------------------------------------------------------------------
def test_nested_primitive_groups() -> None:
    """Tests deep hierarchy: Outer Dashboard Group -> Inner Header + Inner Content + Inner Footer."""
    scene = SceneStoryboardSpec(
        scene_id="scene_nested",
        narration="Here is your complete financial breakdown.",
        root_nodes=[
            StoryboardNode(
                id="dashboard_outer",
                type=CanonicalCapabilityType.GROUP,
                flow=MicroLayoutFlow(flow=ContainerFlow.COLUMN, gap=SemanticSpacing.LG),
                children=[
                    # Header row
                    StoryboardNode(
                        id="header_row",
                        type=CanonicalCapabilityType.GROUP,
                        flow=MicroLayoutFlow(flow=ContainerFlow.ROW, gap=SemanticSpacing.MD),
                        children=[
                            StoryboardNode(
                                id="header_icon",
                                type=CanonicalCapabilityType.ICON,
                                props={"icon_name": "pie-chart"},
                            ),
                            StoryboardNode(
                                id="header_title",
                                type=CanonicalCapabilityType.TEXT,
                                props={"content": "Portfolio Dashboard"},
                            ),
                        ],
                    ),
                    # Content column
                    StoryboardNode(
                        id="content_col",
                        type=CanonicalCapabilityType.GROUP,
                        flow=MicroLayoutFlow(flow=ContainerFlow.COLUMN, gap=SemanticSpacing.SM),
                        children=[
                            StoryboardNode(
                                id="equity_bar",
                                type=CanonicalCapabilityType.BAR,
                                props={"value": 75, "max_value": 100},
                            ),
                            StoryboardNode(
                                id="debt_bar",
                                type=CanonicalCapabilityType.BAR,
                                props={"value": 25, "max_value": 100},
                            ),
                        ],
                    ),
                ],
            )
        ],
        actions=[
            VisualAction(
                action_id="act_reveal",
                target_node_id="dashboard_outer",
                action_type=VisualActionType.ENTER,
                trigger_word="financial",
            )
        ],
    )

    validator = StoryboardValidator()
    result = validator.validate(scene)
    assert result.status == "valid", f"Expected valid, got errors: {result.errors}"
    # Verify nesting depth
    outer = scene.root_nodes[0]
    assert len(outer.children) == 2
    assert len(outer.children[0].children) == 2
    assert len(outer.children[1].children) == 2


# -----------------------------------------------------------------------------
# 6. Trigger-Word Validation
# -----------------------------------------------------------------------------
def test_trigger_word_validation_success() -> None:
    """Punctuation adjacent and exact trigger words pass validation."""
    scene = SceneStoryboardSpec(
        scene_id="scene_tw",
        narration="First, invest ₹50,000 every single month.",
        root_nodes=[
            StoryboardNode(id="n1", type=CanonicalCapabilityType.TEXT, props={"content": "Invest"})
        ],
        actions=[
            VisualAction(
                action_id="a1",
                target_node_id="n1",
                action_type=VisualActionType.ENTER,
                trigger_word="First",  # Has trailing comma in narration
            ),
            VisualAction(
                action_id="a2",
                target_node_id="n1",
                action_type=VisualActionType.PULSE,
                trigger_word="₹50,000",
            ),
        ],
    )
    validator = StoryboardValidator()
    assert validator.validate(scene).status == "valid"


def test_trigger_word_validation_fails_on_missing_word() -> None:
    """Non-existent trigger word is blocked."""
    with pytest.raises(ValidationError, match="was not found in the narration"):
        SceneStoryboardSpec(
            scene_id="scene_fail",
            narration="Only three words here.",
            root_nodes=[
                StoryboardNode(id="n1", type=CanonicalCapabilityType.TEXT, props={"content": "Hi"})
            ],
            actions=[
                VisualAction(
                    action_id="a1",
                    target_node_id="n1",
                    action_type=VisualActionType.ENTER,
                    trigger_word="nonexistent",
                )
            ],
        )


def test_trigger_word_repeated_occurrence_validation() -> None:
    """Occurrence count matches the frequency in the narration."""
    # "money" appears 2 times
    narration = "Save your money before you spend that money carelessly."

    # Occurrence 1 & 2 succeed
    scene_valid = SceneStoryboardSpec(
        scene_id="scene_rep",
        narration=narration,
        root_nodes=[
            StoryboardNode(id="n1", type=CanonicalCapabilityType.TEXT, props={"content": "M1"}),
            StoryboardNode(id="n2", type=CanonicalCapabilityType.TEXT, props={"content": "M2"}),
        ],
        actions=[
            VisualAction(
                action_id="a1",
                target_node_id="n1",
                action_type=VisualActionType.ENTER,
                trigger_word="money",
                trigger_occurrence=1,
            ),
            VisualAction(
                action_id="a2",
                target_node_id="n2",
                action_type=VisualActionType.HIGHLIGHT,
                trigger_word="money",
                trigger_occurrence=2,
            ),
        ],
    )
    assert StoryboardValidator().validate(scene_valid).status == "valid"

    # Occurrence 3 fails because "money" only appears 2 times
    with pytest.raises(ValidationError, match="requests occurrence 3, but only appears 2 time"):
        SceneStoryboardSpec(
            scene_id="scene_rep_fail",
            narration=narration,
            root_nodes=[
                StoryboardNode(id="n1", type=CanonicalCapabilityType.TEXT, props={"content": "M1"})
            ],
            actions=[
                VisualAction(
                    action_id="a1",
                    target_node_id="n1",
                    action_type=VisualActionType.ENTER,
                    trigger_word="money",
                    trigger_occurrence=3,
                )
            ],
        )


# -----------------------------------------------------------------------------
# 7. Prohibition of Downstream Geometry, Frames, and Timestamps
# -----------------------------------------------------------------------------
def test_prohibition_of_pixel_coordinates() -> None:
    """Rejects raw coordinates like x, y, width, height."""
    with pytest.raises(ValidationError, match="Prohibited downstream property"):
        StoryboardNode(
            id="bad_node",
            type=CanonicalCapabilityType.SHAPE,
            props={"x": 300, "y": 450},  # Pixel coordinates prohibited!
        )


def test_prohibition_of_frame_numbers() -> None:
    """Rejects frame numbers like start_frame, duration_frames."""
    with pytest.raises(ValidationError, match="Prohibited downstream property"):
        StoryboardNode(
            id="bad_frame_node",
            type=CanonicalCapabilityType.TEXT,
            props={"start_frame": 45, "content": "Hello"},  # Frame numbers prohibited!
        )


def test_prohibition_of_timestamps() -> None:
    """Rejects timestamps like time_seconds or timestamps."""
    with pytest.raises(ValidationError, match="Prohibited downstream property"):
        StoryboardNode(
            id="bad_time_node",
            type=CanonicalCapabilityType.TEXT,
            props={"timestamp": "00:04.5", "content": "Hello"},  # Timestamps prohibited!
        )


# -----------------------------------------------------------------------------
# 8. Rejection of High-Level Capability Names
# -----------------------------------------------------------------------------
def test_rejection_of_card_or_hero_capability() -> None:
    """Rejects 'card', 'hero', 'comparison' as capability types."""
    with pytest.raises(ValidationError):
        StoryboardNode(
            id="fake_card",
            type="card",  # type: ignore[arg-type]
            props={"title": "My Card"},
        )

    with pytest.raises(ValidationError):
        StoryboardNode(
            id="fake_hero",
            type="hero",  # type: ignore[arg-type]
            props={"metric": "100"},
        )


def test_rejection_of_children_on_non_group_primitive() -> None:
    """Only 'group' primitive can contain child nodes."""
    with pytest.raises(ValidationError, match="Only 'group' primitives may have children"):
        StoryboardNode(
            id="bad_text",
            type=CanonicalCapabilityType.TEXT,
            props={"content": "I am text"},
            children=[
                StoryboardNode(
                    id="child_node",
                    type=CanonicalCapabilityType.TEXT,
                    props={"content": "I should not be here"},
                )
            ],
        )


# -----------------------------------------------------------------------------
# 9. Regression Tests: relationship_type is Semantic Context ONLY
# -----------------------------------------------------------------------------
def test_relationship_type_is_semantic_context_not_deterministic_mapping() -> None:
    """Proves that VisualIntent.relationship_type does NOT prescribe primitives or layouts.

    Case Study: Two different intents with the EXACT SAME relationship_type ('growth').
    - Scenario A (Rent increase 22%): Storyboarder creatively chooses a CENTER group
      with a horizontal progress bar, warning icon, and percentage ticker.
    - Scenario B (15-Year Wealth Compounding): Storyboarder creatively chooses a BOTTOM
      macro-zone with a smooth spline line, peak diamond point, and area fill segment.

    Both must validate successfully without any relationship_type-to-primitive rule.
    """
    # Intent A: Rent growth
    intent_a = VisualIntent(
        intent_id="intent_rent_growth",
        narration_excerpt="Metro house rent increased by twenty-two percent this year alone.",
        what_viewer_must_understand="Metro house rent surged by 22% putting extreme pressure on tenants.",
        relationship_type="growth",  # Same relationship_type
        measurements=[
            QuantitativeMeasurement(raw_value="22%", numeric_value=22.0, unit="%", role="rate")
        ],
        entities=[SemanticEntity(name="Metro House Rent", role="subject")],
    )

    # Scene A: Composed as a centered bar + warning badge + ticker
    scene_a = SceneStoryboardSpec(
        scene_id="scene_rent",
        source_intent_ids=[intent_a.intent_id],
        visual_intent=intent_a,
        narration=intent_a.narration_excerpt,
        macro_zone=MacroScreenZone.CENTER,  # Creative choice: Center
        root_nodes=[
            StoryboardNode(
                id="rent_container",
                type=CanonicalCapabilityType.GROUP,
                flow=MicroLayoutFlow(flow=ContainerFlow.COLUMN, gap=SemanticSpacing.MD),
                style=SemanticStyleIntent(fill_role=SemanticColorRole.SURFACE, radius_role=SemanticRadiusRole.CARD),
                children=[
                    StoryboardNode(
                        id="warning_icon",
                        type=CanonicalCapabilityType.ICON,
                        props={"icon_name": "alert-triangle"},
                        style=SemanticStyleIntent(text_color_role=SemanticColorRole.WARNING),
                    ),
                    StoryboardNode(
                        id="rent_text",
                        type=CanonicalCapabilityType.TEXT,
                        props={"content": "Metro House Rent Surge"},
                        style=SemanticStyleIntent(typography_role=SemanticTypographyRole.SUBHEADLINE),
                    ),
                    StoryboardNode(
                        id="rent_bar",
                        type=CanonicalCapabilityType.BAR,  # Creative choice: Bar primitive
                        props={"value": 22, "max_value": 100, "orientation": "horizontal"},
                        style=SemanticStyleIntent(fill_role=SemanticColorRole.DANGER),
                    ),
                    StoryboardNode(
                        id="rent_pct",
                        type=CanonicalCapabilityType.NUMBER,
                        props={"value": 22, "format": "percent"},
                        style=SemanticStyleIntent(typography_role=SemanticTypographyRole.HEADLINE),
                    ),
                ],
            )
        ],
        actions=[
            VisualAction(
                action_id="act_surge",
                target_node_id="rent_bar",
                action_type=VisualActionType.ENTER,
                trigger_word="twenty-two",
            )
        ],
    )

    # Intent B: 15-Year Wealth Compounding (Also relationship_type='growth'!)
    intent_b = VisualIntent(
        intent_id="intent_wealth_growth",
        narration_excerpt="Over fifteen years, your long-term equity portfolio compounds into ten lakh rupees.",
        what_viewer_must_understand="Long-term patient investing accumulates exponential wealth over time.",
        relationship_type="growth",  # EXACT SAME relationship_type!
        measurements=[
            QuantitativeMeasurement(raw_value="₹10 lakh", numeric_value=10.0, unit="lakh", role="result"),
            QuantitativeMeasurement(raw_value="15 years", numeric_value=15.0, unit="years", role="rate"),
        ],
        entities=[SemanticEntity(name="Equity Portfolio", role="subject")],
    )

    # Scene B: Composed as a bottom-docked trend line + peak marker + area segment
    scene_b = SceneStoryboardSpec(
        scene_id="scene_wealth",
        source_intent_ids=[intent_b.intent_id],
        visual_intent=intent_b,
        narration=intent_b.narration_excerpt,
        macro_zone=MacroScreenZone.BOTTOM,  # Creative choice: Bottom zone (completely different from scene_a)
        root_nodes=[
            StoryboardNode(
                id="wealth_trend_line",
                type=CanonicalCapabilityType.LINE,  # Creative choice: Line primitive
                props={"curve_type": "smooth", "points": [[0, 800], [500, 600], [1200, 200]]},
                style=SemanticStyleIntent(stroke_role=SemanticColorRole.ACCENT),
            ),
            StoryboardNode(
                id="wealth_area_segment",
                type=CanonicalCapabilityType.SEGMENT,  # Creative choice: Segment primitive
                props={"filled": True, "fill_opacity": 0.25},
                style=SemanticStyleIntent(fill_role=SemanticColorRole.ACCENT),
            ),
            StoryboardNode(
                id="wealth_peak_point",
                type=CanonicalCapabilityType.POINT,  # Creative choice: Point primitive
                props={"label": "₹10 Lakh Milestone", "shape": "diamond"},
                style=SemanticStyleIntent(fill_role=SemanticColorRole.SUCCESS),
            ),
            StoryboardNode(
                id="wealth_title",
                type=CanonicalCapabilityType.TEXT,
                props={"content": "15-Year Compounding Trajectory"},
                style=SemanticStyleIntent(typography_role=SemanticTypographyRole.HEADLINE),
            ),
        ],
        actions=[
            VisualAction(
                action_id="act_peak",
                target_node_id="wealth_peak_point",
                action_type=VisualActionType.HIGHLIGHT,
                trigger_word="compounds",
            )
        ],
    )

    validator = StoryboardValidator()

    # Validate Scene A (Growth -> Center Bar & Ticker)
    result_a = validator.validate(scene_a)
    assert result_a.status == "valid", f"Scene A failed validation: {result_a.errors}"
    assert scene_a.macro_zone == MacroScreenZone.CENTER
    node_types_a = {node.type for node in scene_a.root_nodes[0].children}
    assert CanonicalCapabilityType.BAR in node_types_a
    assert CanonicalCapabilityType.LINE not in node_types_a

    # Validate Scene B (Growth -> Bottom Line & Segment)
    result_b = validator.validate(scene_b)
    assert result_b.status == "valid", f"Scene B failed validation: {result_b.errors}"
    assert scene_b.macro_zone == MacroScreenZone.BOTTOM
    node_types_b = {node.type for node in scene_b.root_nodes}
    assert CanonicalCapabilityType.LINE in node_types_b
    assert CanonicalCapabilityType.SEGMENT in node_types_b
    assert CanonicalCapabilityType.BAR not in node_types_b


def test_same_metric_intent_allows_radial_gauge_vs_currency_badge() -> None:
    """Proves that two 'metric' relationship intents can produce completely different primitives.

    - Metric A ('Inflation hit 7%') ➔ Creative Storyboarder chooses a radial gauge ('progress')
    - Metric B ('₹50,000 baseline salary') ➔ Creative Storyboarder chooses a currency ticker ('number')
    """
    intent_inflation = VisualIntent(
        intent_id="intent_inf",
        narration_excerpt="Inflation hit seven percent crossing the safety band.",
        what_viewer_must_understand="Inflation is at 7%.",
        relationship_type="metric",
    )
    scene_inflation = SceneStoryboardSpec(
        scene_id="scene_inf",
        visual_intent=intent_inflation,
        narration=intent_inflation.narration_excerpt,
        macro_zone=MacroScreenZone.RIGHT,
        root_nodes=[
            StoryboardNode(
                id="gauge_node",
                type=CanonicalCapabilityType.PROGRESS,  # Progress primitive for metric!
                props={"progress_kind": "circular", "value": 7, "target": 10},
                style=SemanticStyleIntent(stroke_role=SemanticColorRole.WARNING),
            )
        ],
        actions=[
            VisualAction(
                action_id="act_gauge",
                target_node_id="gauge_node",
                action_type=VisualActionType.ENTER,
                trigger_word="Inflation",
            )
        ],
    )

    intent_salary = VisualIntent(
        intent_id="intent_sal",
        narration_excerpt="Your base salary is fifty thousand rupees.",
        what_viewer_must_understand="Salary is 50,000.",
        relationship_type="metric",
    )
    scene_salary = SceneStoryboardSpec(
        scene_id="scene_sal",
        visual_intent=intent_salary,
        narration=intent_salary.narration_excerpt,
        macro_zone=MacroScreenZone.TOP_LEFT,
        root_nodes=[
            StoryboardNode(
                id="salary_num_node",
                type=CanonicalCapabilityType.NUMBER,  # Number primitive for metric!
                props={"value": 50000, "currency_symbol": "₹", "format": "currency"},
                style=SemanticStyleIntent(typography_role=SemanticTypographyRole.DISPLAY),
            )
        ],
        actions=[
            VisualAction(
                action_id="act_sal",
                target_node_id="salary_num_node",
                action_type=VisualActionType.ENTER,
                trigger_word="salary",
            )
        ],
    )

    validator = StoryboardValidator()
    assert validator.validate(scene_inflation).status == "valid"
    assert validator.validate(scene_salary).status == "valid"
    assert scene_inflation.root_nodes[0].type == CanonicalCapabilityType.PROGRESS
    assert scene_salary.root_nodes[0].type == CanonicalCapabilityType.NUMBER


def test_same_comparison_intent_allows_split_cards_vs_comparative_bars() -> None:
    """Proves that two 'comparison' intents can produce split-cards vs side-by-side bars."""
    intent_split = VisualIntent(
        intent_id="intent_split",
        narration_excerpt="Comparing active income to fixed monthly rent.",
        what_viewer_must_understand="Compare income to rent.",
        relationship_type="comparison",
    )
    scene_split = SceneStoryboardSpec(
        scene_id="scene_split",
        visual_intent=intent_split,
        narration=intent_split.narration_excerpt,
        root_nodes=[
            StoryboardNode(
                id="left_side",
                type=CanonicalCapabilityType.GROUP,
                macro_zone=MacroScreenZone.SPLIT_LEFT,
                children=[StoryboardNode(id="t1", type=CanonicalCapabilityType.TEXT, props={"content": "Salary"})],
            ),
            StoryboardNode(
                id="right_side",
                type=CanonicalCapabilityType.GROUP,
                macro_zone=MacroScreenZone.SPLIT_RIGHT,
                children=[StoryboardNode(id="t2", type=CanonicalCapabilityType.TEXT, props={"content": "Rent"})],
            ),
        ],
        actions=[
            VisualAction(action_id="a1", target_node_id="left_side", action_type=VisualActionType.APPEAR, trigger_word="active"),
        ],
    )

    intent_bars = VisualIntent(
        intent_id="intent_bars",
        narration_excerpt="Compare equity returns against real estate yields.",
        what_viewer_must_understand="Compare stocks vs real estate.",
        relationship_type="comparison",
    )
    scene_bars = SceneStoryboardSpec(
        scene_id="scene_bars",
        visual_intent=intent_bars,
        narration=intent_bars.narration_excerpt,
        macro_zone=MacroScreenZone.CENTER,
        root_nodes=[
            StoryboardNode(
                id="bar_container",
                type=CanonicalCapabilityType.GROUP,
                flow=MicroLayoutFlow(flow=ContainerFlow.ROW, gap=SemanticSpacing.LG),
                children=[
                    StoryboardNode(id="b1", type=CanonicalCapabilityType.BAR, props={"value": 14, "max_value": 20}),
                    StoryboardNode(id="b2", type=CanonicalCapabilityType.BAR, props={"value": 8, "max_value": 20}),
                ],
            )
        ],
        actions=[
            VisualAction(action_id="a2", target_node_id="bar_container", action_type=VisualActionType.ENTER, trigger_word="Compare"),
        ],
    )

    validator = StoryboardValidator()
    assert validator.validate(scene_split).status == "valid"
    assert validator.validate(scene_bars).status == "valid"
    assert scene_split.root_nodes[0].macro_zone == MacroScreenZone.SPLIT_LEFT
    assert scene_bars.root_nodes[0].macro_zone is None  # Inherits center
    assert scene_bars.macro_zone == MacroScreenZone.CENTER


def test_scene_representing_multiple_visual_intents() -> None:
    """Proves that a single SceneStoryboardSpec can represent multiple VisualIntents."""
    intent_1 = "intent_salary_baseline"
    intent_2 = "intent_rent_deduction"

    scene = SceneStoryboardSpec(
        scene_id="scene_combined_income_rent",
        source_intent_ids=[intent_1, intent_2],  # Multiple VisualIntents represented in this scene
        narration="Your nominal salary of fifty thousand rupees gets hit by twenty thousand in rent.",
        macro_zone=MacroScreenZone.CENTER,
        root_nodes=[
            StoryboardNode(
                id="salary_element",
                type=CanonicalCapabilityType.NUMBER,
                props={"value": 50000, "currency_symbol": "₹", "format": "currency"},
            ),
            StoryboardNode(
                id="rent_element",
                type=CanonicalCapabilityType.NUMBER,
                props={"value": 20000, "currency_symbol": "₹", "format": "currency"},
            ),
        ],
        actions=[
            VisualAction(
                action_id="act_salary",
                target_node_id="salary_element",
                action_type=VisualActionType.ENTER,
                trigger_word="salary",
            ),
            VisualAction(
                action_id="act_rent",
                target_node_id="rent_element",
                action_type=VisualActionType.ENTER,
                trigger_word="rent",
            ),
        ],
    )

    validator = StoryboardValidator()
    result = validator.validate(scene)
    assert result.status == "valid"
    assert scene.source_intent_ids == ["intent_salary_baseline", "intent_rent_deduction"]
    assert len(scene.source_intent_ids) == 2


def test_legacy_intent_id_auto_migrates_to_source_intent_ids() -> None:
    """Proves that passing legacy 'intent_id' auto-migrates to 'source_intent_ids'."""
    data = {
        "scene_id": "scene_legacy",
        "intent_id": "legacy_intent_99",  # Legacy single intent_id field
        "narration": "Testing backward compatibility for intent migration.",
        "root_nodes": [
            {"id": "n1", "type": "text", "props": {"content": "Test"}}
        ],
    }
    scene = SceneStoryboardSpec.model_validate(data)
    assert scene.source_intent_ids == ["legacy_intent_99"]


# -----------------------------------------------------------------------------
# 11. Refinement Tests: Relationships, Persistence Continuity, Semantic Names
# -----------------------------------------------------------------------------
def test_explicit_semantic_relationships_valid() -> None:
    """Proves that scenes can define explicit semantic relationships."""
    from domain.storyboard import SemanticRelationship

    scene = SceneStoryboardSpec(
        scene_id="scene_rel",
        narration="Salary grew 10% while rent increased 22%, causing purchasing power to drop.",
        root_nodes=[
            StoryboardNode(id="salary_metric", type=CanonicalCapabilityType.NUMBER, props={"value": 10}),
            StoryboardNode(id="rent_metric", type=CanonicalCapabilityType.NUMBER, props={"value": 22}),
            StoryboardNode(id="purchasing_power_metric", type=CanonicalCapabilityType.NUMBER, props={"value": -3.5}),
        ],
        relationships=[
            SemanticRelationship(
                source_id="salary_metric",
                relation="compared_with",
                target_id="rent_metric",
                visual_representation="side_by_side_contrast",
                description="Comparing salary raise against rent surge",
            ),
            SemanticRelationship(
                source_id="rent_metric",
                relation="contributes_to",
                target_id="purchasing_power_metric",
                visual_representation="downward_pressure_payoff",
            ),
        ],
    )
    validator = StoryboardValidator()
    result = validator.validate(scene)
    assert result.status == "valid"
    assert len(scene.relationships) == 2
    assert scene.relationships[0].relation == "compared_with"
    assert scene.relationships[1].relation == "contributes_to"


def test_banned_template_identifier_rejected() -> None:
    """Proves that node IDs like 'group_comparison' or 'group_card' are rejected by validator."""
    scene = SceneStoryboardSpec(
        scene_id="scene_banned_id",
        narration="Here is a simple financial statement.",
        root_nodes=[
            StoryboardNode(
                id="group_comparison",  # Banned template name in ID
                type=CanonicalCapabilityType.GROUP,
            )
        ],
    )
    validator = StoryboardValidator()
    result = validator.validate(scene)
    assert result.status == "blocked"
    assert any("template composition name" in e for e in result.errors)


def test_cross_scene_persistent_object_re_appear_rejected() -> None:
    """Proves that re-triggering appear/enter on a persistent object from an earlier scene is rejected."""
    scene1 = SceneStoryboardSpec(
        scene_id="scene_1",
        narration="You got a ten percent salary raise.",
        root_nodes=[
            StoryboardNode(
                id="salary_metric",
                type=CanonicalCapabilityType.NUMBER,
                persistence_key="salary_metric_key",
                persistence_scope="cross_scene",
            )
        ],
        actions=[
            VisualAction(
                action_id="act_intro_salary",
                target_node_id="salary_metric",
                action_type=VisualActionType.ENTER,
                trigger_word="salary",
            )
        ],
    )

    # Scene 2 attempts to re-trigger 'appear' on the persistent object
    scene2 = SceneStoryboardSpec(
        scene_id="scene_2",
        narration="That salary raise encounters higher rent.",
        root_nodes=[
            StoryboardNode(
                id="salary_metric",
                type=CanonicalCapabilityType.NUMBER,
                persistence_key="salary_metric_key",
                persistence_scope="cross_scene",
            )
        ],
        actions=[
            VisualAction(
                action_id="act_re_appear_salary",
                target_node_id="salary_metric",
                action_type=VisualActionType.APPEAR,  # RE-TRIGGERING APPEAR IS FORBIDDEN
                trigger_word="salary",
            )
        ],
    )

    project = ProjectStoryboardSpec(scenes=[scene1, scene2])
    validator = StoryboardValidator()
    result = validator.validate(project)
    assert result.status == "blocked"
    assert any("re-triggers 'appear' on persistent object" in e for e in result.errors)


def test_cross_scene_persistent_object_evolve_allowed() -> None:
    """Proves that evolving/transforming a persistent object in later scenes passes validation."""
    scene1 = SceneStoryboardSpec(
        scene_id="scene_1",
        narration="You got a ten percent salary raise.",
        root_nodes=[
            StoryboardNode(
                id="salary_metric",
                type=CanonicalCapabilityType.NUMBER,
                persistence_key="salary_metric_key",
                persistence_scope="cross_scene",
            )
        ],
        actions=[
            VisualAction(
                action_id="act_intro_salary",
                target_node_id="salary_metric",
                action_type=VisualActionType.ENTER,
                trigger_word="salary",
            )
        ],
    )

    # Scene 2 evolves the persistent object using 'transform' and 'highlight'
    scene2 = SceneStoryboardSpec(
        scene_id="scene_2",
        narration="That salary raise encounters higher rent.",
        root_nodes=[
            StoryboardNode(
                id="salary_metric",
                type=CanonicalCapabilityType.NUMBER,
                persistence_key="salary_metric_key",
                persistence_scope="cross_scene",
            ),
            StoryboardNode(
                id="rent_metric",
                type=CanonicalCapabilityType.NUMBER,
            ),
        ],
        actions=[
            VisualAction(
                action_id="act_highlight_salary",
                target_node_id="salary_metric",
                action_type=VisualActionType.HIGHLIGHT,  # ALLOWED
                trigger_word="salary",
            ),
            VisualAction(
                action_id="act_enter_rent",
                target_node_id="rent_metric",
                action_type=VisualActionType.ENTER,  # Brand new entity
                trigger_word="rent",
            ),
        ],
    )

    project = ProjectStoryboardSpec(scenes=[scene1, scene2])
    validator = StoryboardValidator()
    result = validator.validate(project)
    assert result.status == "valid", f"Expected valid, got errors: {result.errors}"

