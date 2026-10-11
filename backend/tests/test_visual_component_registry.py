import pytest
from pydantic import ValidationError

from compiler.models import CanvasConfig
from compiler.world_models import (
    CompiledLifecycleTrack,
    CompiledObjectKind,
    CompiledVisualInstance,
    CompiledWorld,
    LocalRect,
)
from domain.primitives.common import CanonicalCapabilityType
from registries.visual_component_registry import (
    ComponentCategory,
    VisualComponentRegistry,
    VisualComponentRegistryError,
    SurfaceCardProps,
    MetricBlockProps,
    BadgeProps,
    CalloutProps,
    FlowConnectorProps,
    MetricCardProps,
    HeroStatProps,
    ComparisonCardProps,
    ProcessCardProps,
)


def test_registry_contains_five_core_components():
    expected = {"SurfaceCard", "MetricBlock", "Badge", "Callout", "FlowConnector"}
    assert expected.issubset(set(VisualComponentRegistry.COMPONENTS.keys()))
    for comp in expected:
        desc = VisualComponentRegistry.get_descriptor(comp)
        assert desc.component_type == comp
        assert desc.remotion_component == comp


def test_metric_block_preserves_numeric_qualifiers():
    # Test '>57%'
    props_top = VisualComponentRegistry.validate_props("MetricBlock", {
        "qualifier": ">",
        "raw_value": 57.0,
        "display_value": ">57%",
        "unit": "%",
        "label": "Top 10% Wealth Share",
        "subtext": "World Inequality Database",
        "emphasis": "hero",
    })
    assert isinstance(props_top, MetricBlockProps)
    assert props_top.qualifier == ">"
    assert props_top.raw_value == 57.0
    assert props_top.display_value == ">57%"

    # Test '<6%'
    props_bottom = VisualComponentRegistry.validate_props("MetricBlock", {
        "qualifier": "<",
        "raw_value": 6.0,
        "display_value": "<6%",
        "unit": "%",
        "label": "Bottom 50% Wealth Share",
    })
    assert props_bottom.qualifier == "<"
    assert props_bottom.display_value == "<6%"

    # Test '15–30%'
    props_range = VisualComponentRegistry.validate_props("MetricBlock", {
        "display_value": "15–30%",
        "unit": "%",
        "label": "Rental Inflation",
    })
    assert props_range.display_value == "15–30%"
    assert props_range.raw_value is None


def test_unknown_component_raises_error():
    assert not VisualComponentRegistry.is_registered("NonExistentComponent")
    with pytest.raises(VisualComponentRegistryError):
        VisualComponentRegistry.get_descriptor("NonExistentComponent")


def test_deterministic_component_sizing_rules():
    # Badge sizing
    w_badge, h_badge = VisualComponentRegistry.measure("Badge", {"text": "TOP 10% POPULATION"})
    assert h_badge == 32.0
    assert w_badge > 150.0

    # MetricBlock sizing
    w_metric, h_metric = VisualComponentRegistry.measure("MetricBlock", {"emphasis": "hero", "subtext": "Some proof"})
    assert w_metric == 520.0
    assert h_metric == 210.0  # 180 + 30

    # Callout sizing
    w_callout, h_callout = VisualComponentRegistry.measure("Callout", {"text": "A short callout thesis."})
    assert w_callout == 520.0
    assert h_callout >= 90.0

    # SurfaceCard sizing with child sizes
    child_sizes = [(472.0, 32.0), (472.0, 210.0)]
    w_card, h_card = VisualComponentRegistry.measure("SurfaceCard", {}, child_sizes=child_sizes)
    assert w_card == 520.0
    # pad_y(48) + child_h(242) + gap(16) = 306
    assert h_card == 306.0


def test_compiled_visual_instance_validation():
    # Valid component instance
    comp = CompiledVisualInstance(
        object_id="card_1",
        kind=CompiledObjectKind.COMPONENT,
        component_type="SurfaceCard",
        local_geometry=LocalRect(x=80, y=240, width=520, height=340),
        properties={"variant": "elevated", "intent": "accent"},
    )
    assert comp.kind == CompiledObjectKind.COMPONENT
    assert comp.component_type == "SurfaceCard"

    # Invalid: component with primitive_type
    with pytest.raises(ValidationError):
        CompiledVisualInstance(
            object_id="card_bad",
            kind=CompiledObjectKind.COMPONENT,
            component_type="SurfaceCard",
            primitive_type=CanonicalCapabilityType.GROUP,
            local_geometry=LocalRect(x=0, y=0, width=100, height=100),
        )

    # Invalid: unknown component_type
    with pytest.raises(ValidationError):
        CompiledVisualInstance(
            object_id="card_unknown",
            kind=CompiledObjectKind.COMPONENT,
            component_type="FakeCard",
            local_geometry=LocalRect(x=0, y=0, width=100, height=100),
        )


def test_compiled_world_v2_with_component_hierarchy():
    world = CompiledWorld(
        schema_version="2.0",
        world_id="component_test_world",
        canvas_config=CanvasConfig(width=1920, height=1080, fps=30),
        total_duration_frames=300,
        objects={
            "top_card": CompiledVisualInstance(
                object_id="top_card",
                kind=CompiledObjectKind.COMPONENT,
                component_type="SurfaceCard",
                child_object_ids=["top_metric"],
                local_geometry=LocalRect(x=80, y=240, width=520, height=340),
            ),
            "top_metric": CompiledVisualInstance(
                object_id="top_metric",
                kind=CompiledObjectKind.COMPONENT,
                component_type="MetricBlock",
                parent_object_id="top_card",
                local_geometry=LocalRect(x=24, y=24, width=472, height=200),
                properties={"display_value": ">57%", "label": "Wealth Share"},
            ),
        },
        lifecycle_tracks=[
            CompiledLifecycleTrack(object_id="top_card", introduced_frame=0, mode="persistent"),
            CompiledLifecycleTrack(object_id="top_metric", introduced_frame=0, mode="persistent"),
        ],
    )
    assert world.schema_version == "2.0"
    assert "top_card" in world.objects
    assert "top_metric" in world.objects
    assert world.objects["top_metric"].parent_object_id == "top_card"


def test_process_card_optional_title_and_derived_step_numbers():
    # ProcessCard without title should succeed and title defaults to None
    props = VisualComponentRegistry.validate_props("ProcessCard", {
        "steps": [
            {"title": "Repo Rate Hike"},
            {"title": "MCLR Transmission", "detail": "+25 bps"},
        ],
    })
    assert isinstance(props, ProcessCardProps)
    assert props.title is None
    assert len(props.steps) == 2
    assert props.steps[0].step == 1
    assert props.steps[0].title == "Repo Rate Hike"
    assert props.steps[1].step == 2
    assert props.steps[1].detail == "+25 bps"

    # Preserves explicit step numbers when provided
    props_explicit = VisualComponentRegistry.validate_props("ProcessCard", {
        "title": "CUSTOM PROCESS",
        "steps": [
            {"step": 1, "title": "Step One"},
            {"step": 2, "title": "Step Two"},
        ],
    })
    assert isinstance(props_explicit, ProcessCardProps)
    assert props_explicit.title == "CUSTOM PROCESS"
    assert props_explicit.steps[0].step == 1
    assert props_explicit.steps[1].step == 2


def test_unsupported_properties_raise_clear_error():
    # Unsupported property on MetricCard
    with pytest.raises(VisualComponentRegistryError) as exc_info:
        VisualComponentRegistry.validate_props("MetricCard", {
            "label": "TEST",
            "display_value": "123",
            "random_unknown_field": "disallowed",
        })
    err_msg = str(exc_info.value)
    assert "received unsupported properties: ['random_unknown_field']" in err_msg
    assert "Supported properties are:" in err_msg
    assert "display_value" in err_msg
    assert "label" in err_msg


def test_shared_metadata_separation():
    # Shared metadata like macro_zone, role, lifecycle_mode alongside MetricCard props
    props = VisualComponentRegistry.validate_props("MetricCard", {
        "label": "INFLATION",
        "display_value": "6.2%",
        "macro_zone": "center",
        "role": "primary",
        "lifecycle_mode": "persistent",
        "parent_object_id": "root",
        "object_id": "metric_1",
    })
    assert isinstance(props, MetricCardProps)
    assert props.label == "INFLATION"
    assert props.display_value == "6.2%"
    assert not hasattr(props, "macro_zone")

    # SurfaceCard has its own macro_zone field, which should be kept
    card_props = VisualComponentRegistry.validate_props("SurfaceCard", {
        "macro_zone": "top_left",
        "role": "primary",  # role is separated out
    })
    assert isinstance(card_props, SurfaceCardProps)
    assert card_props.macro_zone == "top_left"


def test_minimum_required_fields_across_simplified_components():
    # 1. MetricCard: label, display_value
    mc = VisualComponentRegistry.validate_props("MetricCard", {
        "label": "GDP",
        "display_value": "7.2%",
    })
    assert isinstance(mc, MetricCardProps)
    with pytest.raises(ValidationError):
        VisualComponentRegistry.validate_props("MetricCard", {"label": "GDP"})

    # 2. HeroStat: label, display_value
    hs = VisualComponentRegistry.validate_props("HeroStat", {
        "label": "SAVINGS",
        "display_value": "$50,000",
    })
    assert isinstance(hs, HeroStatProps)
    with pytest.raises(ValidationError):
        VisualComponentRegistry.validate_props("HeroStat", {"display_value": "$50,000"})

    # 3. ComparisonCard: left_label, left_value, right_label, right_value
    cc = VisualComponentRegistry.validate_props("ComparisonCard", {
        "left_label": "BEFORE",
        "left_value": "10%",
        "right_label": "AFTER",
        "right_value": "15%",
    })
    assert isinstance(cc, ComparisonCardProps)
    with pytest.raises(ValidationError):
        VisualComponentRegistry.validate_props("ComparisonCard", {
            "left_label": "BEFORE",
            "left_value": "10%",
            # Missing right side
        })

    # 4. ProcessCard: steps
    pc = VisualComponentRegistry.validate_props("ProcessCard", {
        "steps": [{"title": "Step 1"}, {"title": "Step 2"}],
    })
    assert isinstance(pc, ProcessCardProps)
    with pytest.raises(ValidationError):
        VisualComponentRegistry.validate_props("ProcessCard", {})

    # 5. Callout: text
    co = VisualComponentRegistry.validate_props("Callout", {"text": "Key takeaway"})
    assert isinstance(co, CalloutProps)
    with pytest.raises(ValidationError):
        VisualComponentRegistry.validate_props("Callout", {})

    # 6. FlowConnector: source_id, target_id
    fc = VisualComponentRegistry.validate_props("FlowConnector", {
        "source_id": "card_a",
        "target_id": "card_b",
    })
    assert isinstance(fc, FlowConnectorProps)
    with pytest.raises(ValidationError):
        VisualComponentRegistry.validate_props("FlowConnector", {"source_id": "card_a"})


def test_metric_card_and_hero_stat_value_alias_normalization():
    # MetricCard with 'value' alias
    mc = VisualComponentRegistry.validate_props("MetricCard", {
        "label": "MCLR",
        "display_value": "8.5%",
        "value": 8.5,
    })
    assert isinstance(mc, MetricCardProps)
    assert mc.raw_value == 8.5

    # HeroStat with 'value' alias
    hs = VisualComponentRegistry.validate_props("HeroStat", {
        "label": "SUBSIDY",
        "display_value": "₹1,500 CRORE",
        "value": 1500.0,
    })
    assert isinstance(hs, HeroStatProps)
    assert hs.raw_value == 1500.0


def test_trend_line_chart_validation_and_measurement():
    from registries.visual_component_registry import TrendLineChartProps

    # Valid TrendLineChart props
    props = {
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
        "subtext": "Historical annual averages",
    }
    validated = VisualComponentRegistry.validate_props("TrendLineChart", props)
    assert isinstance(validated, TrendLineChartProps)
    assert validated.header == "USD / INR 5-YEAR TRAJECTORY"
    assert len(validated.data_points) == 5
    # Auto-derived intent for "down" trend
    assert validated.intent == "danger"
    assert validated.highlight_point.label == "2024 PEAK"

    # Measurement rule
    w, h = VisualComponentRegistry.measure("TrendLineChart", props, available_width=900.0)
    assert w == 860.0
    assert h == 400.0  # 380 + 20 for subtext

    # Title alias to header normalization
    alias_props = {
        "title": "REPO RATE CYCLE",
        "data_points": [
            {"label": "Q1", "value": 4.0},
            {"label": "Q4", "value": 6.5},
        ],
        "trend": "up",
    }
    validated_alias = VisualComponentRegistry.validate_props("TrendLineChart", alias_props)
    assert isinstance(validated_alias, TrendLineChartProps)
    assert validated_alias.header == "REPO RATE CYCLE"
    assert validated_alias.intent == "accent"  # auto-derived for "up"

    # Rejection of fewer than 2 points when points are explicitly provided
    with pytest.raises(ValidationError):
        VisualComponentRegistry.validate_props("TrendLineChart", {
            "header": "SINGLE POINT",
            "data_points": [{"label": "2024", "value": 88.5}],
            "trend": "up",
        })

    # Optional data_points: omitted completely
    no_points_props = {
        "header": "INFLOW VS OUTFLOW",
        "trend": "up",
        "intent": "accent",
    }
    validated_no_points = VisualComponentRegistry.validate_props("TrendLineChart", no_points_props)
    assert isinstance(validated_no_points, TrendLineChartProps)
    assert validated_no_points.header == "INFLOW VS OUTFLOW"
    assert validated_no_points.data_points == []
    assert validated_no_points.trend == "up"
    assert validated_no_points.intent == "accent"

    # Alias: 'points' alias mapped to 'data_points'
    points_alias_props = {
        "header": "POINTS ALIAS TEST",
        "points": [
            {"label": "2020", "value": 10.0},
            {"label": "2024", "value": 50.0},
        ],
        "trend": "up",
    }
    validated_points_alias = VisualComponentRegistry.validate_props("TrendLineChart", points_alias_props)
    assert isinstance(validated_points_alias, TrendLineChartProps)
    assert len(validated_points_alias.data_points) == 2
    assert validated_points_alias.data_points[0].label == "2020"


def test_ranked_bar_chart_validation_and_measurement():
    from registries.visual_component_registry import RankedBarChartProps

    # Valid RankedBarChart with minimal and optional fields
    props = {
        "header": "CRUDE OIL IMPORT DEPENDENCY",
        "bars": [
            {"label": "India", "value": 87.0, "display_value": "87%", "intent": "danger", "tag": "HIGHEST"},
            {"label": "China", "value": 72.0},  # display_value omitted -> auto-derived
            {"label": "US", "value": 20.0, "display_value": "20%", "intent": "neutral"},
        ],
        "benchmark_value": 50.0,
        "benchmark_label": "Global Avg",
        "subtext": "Official import figures",
    }
    validated = VisualComponentRegistry.validate_props("RankedBarChart", props)
    assert isinstance(validated, RankedBarChartProps)
    assert validated.header == "CRUDE OIL IMPORT DEPENDENCY"
    assert len(validated.bars) == 3
    # Check auto-derived display_value
    assert validated.bars[1].display_value == "72"
    assert validated.bars[0].tag == "HIGHEST"
    assert validated.benchmark_value == 50.0

    # Measurement rule
    w, h = VisualComponentRegistry.measure("RankedBarChart", props, available_width=900.0)
    assert w == 860.0
    # 100 + 3*48 (144) + 20 (subtext) + 15 (benchmark) = 279.0
    assert h == 279.0

    # Title alias normalization
    alias_props = {
        "title": "ASSET RETURNS",
        "bars": [
            {"label": "Equities", "value": 14.0},
            {"label": "Cash", "value": 3.0},
        ],
    }
    validated_alias = VisualComponentRegistry.validate_props("RankedBarChart", alias_props)
    assert isinstance(validated_alias, RankedBarChartProps)
    assert validated_alias.header == "ASSET RETURNS"

    # Rejection of fewer than 2 bars
    with pytest.raises(ValidationError):
        VisualComponentRegistry.validate_props("RankedBarChart", {
            "header": "TOO FEW",
            "bars": [{"label": "Single", "value": 10.0}],
        })


def test_allocation_donut_validation_and_measurement():
    props = {
        "header": "TARGET ASSET ALLOCATION",
        "slices": [
            {"label": "Equities", "value": 60.0, "tag": "Core"},
            {"label": "Fixed Income", "value": 30.0},  # auto-derived display_value
            {"label": "Gold", "value": 10.0, "display_value": "10%", "intent": "warning"},
        ],
        "center_label": "TOTAL ASSETS",
        "center_value": "100%",
        "subtext": "Recommended balanced distribution",
    }
    validated = VisualComponentRegistry.validate_props("AllocationDonut", props)
    assert validated.header == "TARGET ASSET ALLOCATION"
    assert len(validated.slices) == 3
    assert validated.slices[1].display_value == "30"
    assert validated.center_value == "100%"
    assert validated.center_label == "TOTAL ASSETS"

    # Measurement rule
    w, h = VisualComponentRegistry.measure("AllocationDonut", props, available_width=900.0)
    assert w == 860.0
    # max(360, 120 + 3*46 = 258) + 20 subtext = 380.0
    assert h == 380.0

    # Title & segments alias normalization
    alias_props = {
        "title": "REVENUE STREAMS",
        "segments": [
            {"label": "Subscription", "value": 70.0},
            {"label": "Ads", "value": 30.0},
        ],
    }
    validated_alias = VisualComponentRegistry.validate_props("AllocationDonut", alias_props)
    assert validated_alias.header == "REVENUE STREAMS"
    assert len(validated_alias.slices) == 2

    # Rejection of fewer than 2 slices
    with pytest.raises(ValidationError):
        VisualComponentRegistry.validate_props("AllocationDonut", {
            "header": "SINGLE SLICE",
            "slices": [{"label": "Only One", "value": 100.0}],
        })


def test_waterfall_bridge_validation_and_measurement():
    props = {
        "header": "REVENUE TO NET PROFIT BRIDGE",
        "steps": [
            {"label": "Gross Revenue", "value": 100.0, "is_total": True},
            {"label": "COGS", "value": -40.0},  # auto-derived display_value
            {"label": "OpEx", "value": -25.0, "display_value": "-₹25 Cr"},
            {"label": "Net Profit", "value": 35.0, "is_total": True},
        ],
        "subtext": "FY24 Corporate margin breakdown",
    }
    validated = VisualComponentRegistry.validate_props("WaterfallBridge", props)
    assert validated.header == "REVENUE TO NET PROFIT BRIDGE"
    assert len(validated.steps) == 4
    assert validated.steps[0].is_total is True
    assert validated.steps[1].display_value == "-40"
    assert validated.steps[2].display_value == "-₹25 Cr"

    # Measurement rule
    w, h = VisualComponentRegistry.measure("WaterfallBridge", props, available_width=900.0)
    assert w == 880.0
    assert h == 420.0  # 400 + 20 subtext

    # Title alias normalization
    alias_props = {
        "title": "SALARY DEDUCTIONS BRIDGE",
        "steps": [
            {"label": "CTC", "value": 12.0, "is_total": True},
            {"label": "PF & Tax", "value": -3.0},
            {"label": "In Hand", "value": 9.0, "is_total": True},
        ],
    }
    validated_alias = VisualComponentRegistry.validate_props("WaterfallBridge", alias_props)
    assert validated_alias.header == "SALARY DEDUCTIONS BRIDGE"

    # Rejection of fewer than 3 steps
    with pytest.raises(ValidationError):
        VisualComponentRegistry.validate_props("WaterfallBridge", {
            "header": "TOO SHORT",
            "steps": [
                {"label": "Start", "value": 100.0},
                {"label": "End", "value": 100.0},
            ],
        })






