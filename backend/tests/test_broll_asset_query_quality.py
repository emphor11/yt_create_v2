"""Unit tests for broll_caption asset_query generation, schema validation, and fallback mechanisms."""
import pytest

from domain.visual_intent import SemanticEntity, VisualIntent
from domain.composition_plan import CompositionBeat
from registries.composition_registry import CompositionRegistry
from engines.composition_planner_engine import (
    CompositionPlannerEngine,
    build_fallback_asset_query,
    is_valid_asset_query,
    _make_fallback_beat,
)
from engines.composition_assembly_engine import CompositionAssemblyEngine
from providers.llm_provider import LLMJsonRequest, LLMJsonResponse, LLMProviderMetadata


class MockLLMProvider:
    def __init__(self, payload: dict):
        self.payload = payload

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        return LLMJsonResponse(
            payload=self.payload,
            metadata=LLMProviderMetadata(provider="mock-test", model="mock-test"),
        )


def test_broll_caption_schema_requires_asset_query() -> None:
    """Verifies that CompositionRegistry schema requires asset_query specifically for broll_caption."""
    schema = CompositionRegistry.build_planner_response_schema()
    branches = schema["anyOf"]

    broll_branches = [
        b for b in branches
        if b.get("properties", {}).get("composition_id", {}).get("enum") == ["broll_caption"]
    ]
    assert len(broll_branches) == 1
    broll_branch = broll_branches[0]

    assert "asset_query" in broll_branch["required"]
    asset_query_prop = broll_branch["properties"]["asset_query"]
    assert asset_query_prop["type"] == "string"
    assert "nullable" not in asset_query_prop or asset_query_prop.get("nullable") is False


def test_non_broll_compositions_schema_optional_asset_query() -> None:
    """Verifies that non-broll compositions do NOT require asset_query and allow null."""
    schema = CompositionRegistry.build_planner_response_schema()
    branches = schema["anyOf"]

    for b in branches:
        comp_enum = b.get("properties", {}).get("composition_id", {}).get("enum")
        if comp_enum and comp_enum[0] != "broll_caption":
            assert "asset_query" not in b["required"]
            assert b["properties"]["asset_query"].get("nullable") is True


def test_is_valid_asset_query_accepts_concrete_search_terms() -> None:
    """Verifies valid concrete stock-media queries are accepted."""
    valid_queries = [
        "car dealership showroom",
        "mechanic changing tire",
        "person reviewing bank loan",
        "driver filling fuel",
        "luxury car interior",
        "car insurance paperwork",
        "person calculating expenses",
        "used car showroom",
        "car finance paperwork",
        "hand holding car keys",
    ]
    for q in valid_queries:
        assert is_valid_asset_query(q) is True, f"Failed for valid query: {q}"


def test_is_valid_asset_query_rejects_sentences_and_viewer_understands() -> None:
    """Verifies sentences, 'viewer understands...' phrases, and truncated fragments are rejected."""
    invalid_queries = [
        None,
        "",
        "   ",
        "no",
        "Viewer understands how an auto loan is framed as a manageable tool.",
        "Viewer realizes the financial pressure of ownership",
        "Viewer grasps the concept of a long-term loan",
        "The monthly installment is only the visible surface of a muc",
        "While you are paying off the loan, the vehicle itself is mov",
        "This is a complete sentence explaining that car loans are bad.",
        "Opportunity cost of capital in modern markets;",
        "Why you should never buy a new car from a dealer?",
    ]
    for q in invalid_queries:
        assert is_valid_asset_query(q) is False, f"Should have failed for invalid query: {q}"


def test_build_fallback_asset_query_from_entities() -> None:
    """Verifies entity-driven concrete visual query generation."""
    intent = VisualIntent(
        intent_id="intent_test_01",
        narration_excerpt="Standard servicing costs triple.",
        what_viewer_must_understand="Tire replacement and maintenance costs are high.",
        key_values=[],
        relationship_type="statement",
        entities=[SemanticEntity(name="Replacement Tire", role="subject", category="asset")],
    )
    query = build_fallback_asset_query(intent, topic="car financing")
    assert query == "mechanic replacing tire"


def test_build_fallback_asset_query_from_narration_clusters() -> None:
    """Verifies keyword-based fallback generation for dealership, fuel, insurance, loan, etc."""
    test_cases = [
        ("Dealerships exploit this gap by shifting the conversation to EMI.", "car dealership showroom"),
        ("When you factor in mandatory comprehensive insurance and road taxes.", "car insurance paperwork"),
        ("Driver stops at the gas pump for routine fuel.", "driver filling car fuel"),
        ("The vehicle transforms into a luxury lifestyle creep symbol.", "luxury car interior"),
        ("Stretching the loan multiplies the interest you pay to the bank.", "car loan paperwork"),
        ("Surplus cash invested into an index fund compounds over time.", "person reviewing investments"),
        ("Those hidden costs cannibalize your monthly budget and savings.", "person calculating expenses"),
        ("Purchasing a certified pre-owned car absorbs the initial hit.", "used car showroom"),
    ]
    for narration, expected in test_cases:
        intent = VisualIntent(
            intent_id="intent_cluster",
            narration_excerpt=narration,
            what_viewer_must_understand=f"Understanding about {narration[:20]}",
            key_values=[],
            relationship_type="statement",
        )
        assert build_fallback_asset_query(intent, topic="car financing") == expected


def test_make_fallback_beat_never_truncates_narration() -> None:
    """Verifies that _make_fallback_beat produces a concrete query and NEVER narration_excerpt[:60]."""
    long_narration = "The monthly installment is only the visible surface of a much larger financial drain."
    # 'statement' is the correct relationship_type here: the narration makes a claim
    # with no quantitative structure (no measurements, no calculation operands/result).
    intent = VisualIntent(
        intent_id="intent_02_01",
        narration_excerpt=long_narration,
        what_viewer_must_understand="The monthly installment is only the visible surface of a much larger financial drain.",
        key_values=["₹25,000"],
        relationship_type="statement",
    )
    beat = _make_fallback_beat(intent, beat_id="beat_02_01", fallback_reason="validation_error", topic="Car Loans")

    assert beat.composition_id == "broll_caption"
    assert beat.asset_query != long_narration[:60]
    assert "installment is only" not in beat.asset_query
    assert beat.asset_query in ("car loan paperwork", "person calculating expenses", "car finance paperwork")


def test_composition_planner_handles_null_or_invalid_asset_query_gracefully() -> None:
    """When the LLM returns broll_caption with null or an explanatory sentence in asset_query, engine self-heals."""
    intent = VisualIntent(
        intent_id="intent_01_01",
        narration_excerpt="Dealerships exploit this gap immediately by shifting focus to the EMI.",
        what_viewer_must_understand="Viewer understands how an auto loan is framed as a manageable tool.",
        key_values=[],
        relationship_type="statement",
    )
    bad_llm_payload = {
        "status": "ok",
        "composition_id": "broll_caption",
        "variant": "statement",
        "composition_data": {
            "caption": "Viewer understands how an auto loan is framed as a manageable tool.",
            "emphasis_phrase": None,
        },
        "asset_requirement": "optional_broll",
        "asset_query": "Viewer understands how an auto loan is framed as a manageable tool.",
        "trigger_word": "Dealerships",
        "visual_goal": "Viewer understands how an auto loan is framed as a manageable tool.",
    }
    provider = MockLLMProvider(bad_llm_payload)
    engine = CompositionPlannerEngine(provider)

    result = engine.run(intent=intent, beat_id="beat_01_01", topic="Car Loans")
    assert result.beat.composition_id == "broll_caption"
    assert result.beat.asset_query != "Viewer understands how an auto loan is framed as a manageable tool."
    assert is_valid_asset_query(result.beat.asset_query) is True
    assert result.beat.asset_query == "car dealership showroom"


def test_composition_planner_nulls_asset_query_for_infographics() -> None:
    """Infographic compositions must strictly have asset_query=None even if LLM generated a string."""
    from domain.visual_intent import QuantitativeMeasurement
    intent = VisualIntent(
        intent_id="intent_01_02",
        narration_excerpt="40% of salary locked in car payment.",
        what_viewer_must_understand="40% of salary is committed.",
        key_values=["40%"],
        relationship_type="metric",
        measurements=[
            QuantitativeMeasurement(raw_value="40%", metric_name="Salary Locked in Car", role="input")
        ],
    )
    payload = {
        "status": "ok",
        "composition_id": "metric_hero",
        "variant": "hero",
        "composition_data": {
            "value": "40%",
            "label": "Salary Locked in Car",
        },
        "asset_requirement": "none",
        "asset_query": "car dealership showroom",
        "trigger_word": None,
        "visual_goal": "Show 40% salary locked.",
    }
    provider = MockLLMProvider(payload)
    engine = CompositionPlannerEngine(provider)

    result = engine.run(intent=intent, beat_id="beat_01_02")
    assert result.beat.composition_id == "metric_hero"
    assert result.beat.asset_query is None


def test_assembly_engine_resolves_safe_query() -> None:
    """Verifies that CompositionAssemblyEngine._resolve_safe_stock_query cleanses queries."""
    engine = CompositionAssemblyEngine(fps=30)

    # 1. Clean query passes through
    assert engine._resolve_safe_stock_query("car dealership showroom", "Narration about cars") == "car dealership showroom"

    # 2. 'Viewer understands' is sanitized
    sanitized = engine._resolve_safe_stock_query(
        "Viewer understands how an auto loan is framed as a manageable tool.",
        "When you buy from a dealership and get a loan.",
    )
    assert sanitized == "car dealership showroom"

    # 3. Truncated sentence fragment is sanitized
    sanitized2 = engine._resolve_safe_stock_query(
        "The monthly installment is only the visible surface of a muc",
        "When you factor in fuel and insurance expenses.",
    )
    assert sanitized2 in ("car insurance paperwork", "driver filling car fuel", "person calculating expenses")
