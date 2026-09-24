"""Tests for CompositionRegistry."""
import pytest

from registries.composition_registry import (
    AssetRequirement,
    BrollCaptionData,
    CalculationStoryData,
    CauseEffectData,
    CompositionRegistry,
    MetricHeroData,
    MultiFactorPressureData,
    TimeDecayData,
)


# --- Registration & lookup ---

def test_all_initial_compositions_are_registered() -> None:
    registered = CompositionRegistry.all_ids()
    assert "metric_hero" in registered
    assert "calculation_story" in registered
    assert "cause_effect" in registered
    assert "comparison_split" in registered
    assert "ranked_list" in registered
    assert "process_flow" in registered
    assert "time_decay" in registered
    assert "multi_factor_pressure" in registered
    assert "broll_caption" in registered


def test_get_returns_none_for_unknown_id() -> None:
    assert CompositionRegistry.get("totally_made_up") is None


def test_is_registered_true_for_known_ids() -> None:
    for cid in [
        "metric_hero", "calculation_story", "cause_effect", "comparison_split",
        "ranked_list", "process_flow", "time_decay", "multi_factor_pressure", "broll_caption"
    ]:
        assert CompositionRegistry.is_registered(cid) is True


def test_is_registered_false_for_unknown_id() -> None:
    assert CompositionRegistry.is_registered("InflationDamage") is False


# --- Composition data validation ---

def test_validate_metric_hero_valid() -> None:
    ok, errors, normalized = CompositionRegistry.validate_composition_data(
        "metric_hero",
        {"value": "₹50 lakh", "label": "Starting Retirement Portfolio"},
    )
    assert ok is True
    assert errors == []
    assert normalized["value"] == "₹50 lakh"


def test_validate_metric_hero_missing_required_field() -> None:
    ok, errors, _ = CompositionRegistry.validate_composition_data(
        "metric_hero",
        {"value": "₹50 lakh"},  # missing "label"
    )
    assert ok is False
    assert len(errors) > 0


def test_validate_calculation_story_valid() -> None:
    ok, errors, normalized = CompositionRegistry.validate_composition_data(
        "calculation_story",
        {
            "input_label": "Portfolio",
            "input_value": "₹50 lakh",
            "operation_label": "×",
            "rate_label": "4% withdrawal rate",
            "result_label": "Annual Income",
            "result_value": "₹2 lakh",
        },
    )
    assert ok is True
    assert errors == []


def test_validate_cause_effect_valid() -> None:
    ok, errors, _ = CompositionRegistry.validate_composition_data(
        "cause_effect",
        {
            "causes": [{"label": "High Inflation", "value": "7%"}],
            "connector": "leads to",
            "outcome_label": "Retirement Risk",
        },
    )
    assert ok is True
    assert errors == []


def test_validate_time_decay_valid() -> None:
    ok, errors, _ = CompositionRegistry.validate_composition_data(
        "time_decay",
        {
            "fixed_amount": "₹2 lakh",
            "amount_label": "Annual Withdrawal",
            "time_period": "15 years",
            "emphasis": "purchasing_power_decline",
        },
    )
    assert ok is True
    assert errors == []


def test_validate_multi_factor_pressure_valid() -> None:
    ok, errors, _ = CompositionRegistry.validate_composition_data(
        "multi_factor_pressure",
        {
            "factors": [
                {"label": "High Inflation", "value": "7%", "severity": "high"},
                {"label": "Weak Returns", "value": "3%", "severity": "medium"},
            ],
            "combined_label": "Combined Retirement Risk",
            "combined_severity": "critical",
        },
    )
    assert ok is True
    assert errors == []


def test_validate_broll_caption_valid() -> None:
    ok, errors, _ = CompositionRegistry.validate_composition_data(
        "broll_caption",
        {"caption": "The same ₹2 lakh buys less every year."},
    )
    assert ok is True
    assert errors == []


def test_validate_comparison_split_valid() -> None:
    ok, errors, _ = CompositionRegistry.validate_composition_data(
        "comparison_split",
        {
            "left_role": "Option A",
            "left_value": "10%",
            "right_role": "Option B",
            "right_value": "20%",
            "comparison_label": "RETURNS",
        },
    )
    assert ok is True
    assert errors == []


def test_validate_ranked_list_valid() -> None:
    ok, errors, _ = CompositionRegistry.validate_composition_data(
        "ranked_list",
        {
            "header_label": "TOP EXPENSES",
            "items": [
                {"title": "Rent", "value": "₹50k"},
                {"title": "EMI", "value": "₹30k"},
            ],
        },
    )
    assert ok is True
    assert errors == []


def test_validate_process_flow_valid() -> None:
    ok, errors, _ = CompositionRegistry.validate_composition_data(
        "process_flow",
        {
            "header_label": "FLOW",
            "steps": [
                {"title": "Step 1"},
                {"title": "Step 2"},
            ],
        },
    )
    assert ok is True
    assert errors == []


def test_validate_unknown_composition_id_returns_error() -> None:
    ok, errors, _ = CompositionRegistry.validate_composition_data(
        "invented_composition",
        {"some": "data"},
    )
    assert ok is False
    assert any("Unknown composition_id" in e for e in errors)


# --- Prompt generation ---

def test_get_planner_prompt_section_contains_all_ids() -> None:
    section = CompositionRegistry.get_planner_prompt_section()
    for cid in CompositionRegistry.all_ids():
        assert cid in section


def test_get_planner_prompt_section_is_non_empty() -> None:
    section = CompositionRegistry.get_planner_prompt_section()
    assert len(section) > 100


# --- Schema generation ---

def test_build_planner_response_schema_contains_all_ids() -> None:
    schema = CompositionRegistry.build_planner_response_schema()
    registered_ids = CompositionRegistry.all_ids()
    assert len(schema["anyOf"]) == len(registered_ids) + 1

    found_ids = set()
    for branch in schema["anyOf"]:
        if branch.get("properties", {}).get("status", {}).get("enum") == ["ok"]:
            cid_enum = branch["properties"]["composition_id"]["enum"]
            assert len(cid_enum) == 1
            found_ids.add(cid_enum[0])

    assert found_ids == set(registered_ids)


def test_build_planner_response_schema_has_fallback_branch() -> None:
    schema = CompositionRegistry.build_planner_response_schema()
    fallback_branches = [
        b for b in schema["anyOf"]
        if b.get("properties", {}).get("status", {}).get("enum") == ["no_suitable_composition"]
    ]
    assert len(fallback_branches) == 1
    fallback_branch = fallback_branches[0]
    assert "reason" in fallback_branch["properties"]
    assert fallback_branch["required"] == ["status", "reason"]


def test_all_compositions_have_concrete_data_schemas() -> None:
    for cid in CompositionRegistry.all_ids():
        schema = CompositionRegistry.get_data_schema(cid)
        assert schema is not None, f"Schema missing for {cid}"
        assert schema.get("type") == "object", f"Schema type not object for {cid}"
        assert "properties" in schema, f"properties missing in {cid} schema"
        assert len(schema["properties"]) > 0, f"properties empty in {cid} schema"
        assert "required" in schema, f"required missing in {cid} schema"
        assert len(schema["required"]) > 0, f"required list empty in {cid} schema"
        # Must have no unresolved refs or defs
        import json
        schema_str = json.dumps(schema)
        assert "$defs" not in schema_str, f"$defs found in {cid} schema"
        assert "$ref" not in schema_str, f"$ref found in {cid} schema"
        assert "additionalProperties" not in schema_str, f"additionalProperties found in {cid} schema"


def test_calculation_story_schema_properties() -> None:
    schema = CompositionRegistry.get_data_schema("calculation_story")
    assert schema is not None
    required = schema["required"]
    expected_required = [
        "input_label", "input_value", "result_label", "result_value",
    ]
    for field in expected_required:
        assert field in required, f"{field} must be required in calculation_story"
        assert field in schema["properties"], f"{field} must be in calculation_story properties"

    # Optional fields should be in properties but NOT in required
    optional_fields = [
        "operation_label", "rate_label", "note", "operation_type",
        "variant", "polarity", "timeframe", "secondary_label", "secondary_value",
    ]
    for field in optional_fields:
        assert field in schema["properties"], f"{field} must be in calculation_story properties"
        assert field not in required, f"{field} must NOT be required in calculation_story"


def test_validate_calculation_story_valid_without_rate_or_operation() -> None:
    ok, errors, normalized = CompositionRegistry.validate_composition_data(
        "calculation_story",
        {
            "input_label": "Starting Salary",
            "input_value": "₹50,000",
            "result_label": "Final Salary",
            "result_value": "₹2,00,000",
        },
    )
    assert ok is True
    assert errors == []
    assert normalized["input_label"] == "Starting Salary"
    assert normalized["result_value"] == "₹2,00,000"
    assert normalized.get("operation_label") is None
    assert normalized.get("rate_label") is None


def test_validate_calculation_story_with_secondary_metrics() -> None:
    ok, errors, normalized = CompositionRegistry.validate_composition_data(
        "calculation_story",
        {
            "input_label": "Monthly SIP",
            "input_value": "₹10,000",
            "operation_label": "→",
            "rate_label": "12% return over 15 years",
            "result_label": "Total Corpus",
            "result_value": "₹50 Lakh",
            "secondary_label": "Total Invested",
            "secondary_value": "₹18 Lakh",
            "timeframe": "15 Years",
            "operation_type": "growth",
        },
    )
    assert ok is True
    assert errors == []
    assert normalized["secondary_label"] == "Total Invested"
    assert normalized["secondary_value"] == "₹18 Lakh"
    assert normalized["operation_type"] == "growth"


def test_metric_hero_schema_properties() -> None:
    schema = CompositionRegistry.get_data_schema("metric_hero")
    assert schema is not None
    required = schema["required"]
    assert "value" in required
    assert "label" in required
    assert "context" in schema["properties"]
    assert "emphasis" in schema["properties"]
    assert "context" not in required


def test_cause_effect_schema_properties() -> None:
    schema = CompositionRegistry.get_data_schema("cause_effect")
    assert schema is not None
    required = schema["required"]
    assert "causes" in required
    assert "connector" in required
    assert "outcome_label" in required
    causes_items = schema["properties"]["causes"]["items"]
    assert causes_items["type"] == "object"
    assert "label" in causes_items["required"]


def test_time_decay_schema_properties() -> None:
    schema = CompositionRegistry.get_data_schema("time_decay")
    assert schema is not None
    required = schema["required"]
    for field in ["amount_label", "time_period"]:
        assert field in required
    assert "fixed_amount" in schema["properties"]
    assert "fixed_amount" not in required
    assert "decay_type" in schema["properties"]
    assert "emphasis" in schema["properties"]


def test_validate_time_decay_valid_without_fixed_amount() -> None:
    ok, errors, normalized = CompositionRegistry.validate_composition_data(
        "time_decay",
        {
            "amount_label": "New Car Value",
            "time_period": "first year",
            "drop_rate": "15%",
            "emphasis": "single_period_drop",
            "variant": "single_period_drop",
            "decay_type": "single_period",
        },
    )
    assert ok is True
    assert errors == []
    assert normalized["amount_label"] == "New Car Value"
    assert normalized["drop_rate"] == "15%"
    assert normalized["fixed_amount"] is None


def test_multi_factor_pressure_schema_properties() -> None:
    schema = CompositionRegistry.get_data_schema("multi_factor_pressure")
    assert schema is not None
    required = schema["required"]
    assert "factors" in required
    assert "combined_label" in required
    assert "combined_severity" in required
    factors_items = schema["properties"]["factors"]["items"]
    assert factors_items["type"] == "object"
    assert "label" in factors_items["required"]


def test_broll_caption_schema_properties() -> None:
    schema = CompositionRegistry.get_data_schema("broll_caption")
    assert schema is not None
    required = schema["required"]
    assert "caption" in required
    assert "emphasis_phrase" in schema["properties"]
    assert "author" in schema["properties"]
    assert "emphasis_phrase" not in required


# --- Asset requirement ---

def test_metric_hero_requires_no_asset() -> None:
    defn = CompositionRegistry.get("metric_hero")
    assert defn is not None
    assert defn.asset_requirement == AssetRequirement.NONE


def test_broll_caption_requires_optional_broll() -> None:
    defn = CompositionRegistry.get("broll_caption")
    assert defn is not None
    assert defn.asset_requirement == AssetRequirement.OPTIONAL_BROLL


# --- Fallback component mapping ---

def test_all_compositions_have_fallback_component() -> None:
    for cid in CompositionRegistry.all_ids():
        defn = CompositionRegistry.get(cid)
        assert defn is not None
        assert defn.fallback_component_id, f"{cid} missing fallback_component_id"


def test_fallback_component_ids_are_legacy_components() -> None:
    """Fallback components must be from the existing legacy registry."""
    legacy_components = {
        "NumberCounter", "Charts", "SplitComparison", "KPIGrid", "Typography",
        "ProcessFlow", "ProgressiveList", "Timeline", "RankedList", "DataTable",
        "BeforeAfter", "QuoteCallout", "IconAnimation", "StockVideo", "StockImage",
    }
    for cid in CompositionRegistry.all_ids():
        defn = CompositionRegistry.get(cid)
        assert defn is not None
        assert defn.fallback_component_id in legacy_components, (
            f"{cid}.fallback_component_id='{defn.fallback_component_id}' "
            f"is not a known legacy component."
        )
