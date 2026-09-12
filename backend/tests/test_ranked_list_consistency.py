from typing import Any
import pytest
from registries.composition_registry import CompositionRegistry, RankedListData, RankedItem
from engines.composition_planner_engine import (
    build_candidate_composition_data,
    merge_factual_and_presentation_data,
)
from engines.video_assembly.composition_resolver import CompositionResolver
from domain.visual_intent import VisualIntent


def test_ranked_list_data_accepts_all_fields() -> None:
    data = RankedListData(
        header_label="TOP WEALTH DESTROYERS",
        variant="dominance",
        footer_label="Annual compounded drag over 20 years",
        show_bars=True,
        items=[
            RankedItem(
                title="Lifestyle Inflation",
                rank=1,
                value="42%",
                numeric_value=42.0,
                badge="PRIMARY LEADER",
                change="+2",
            ),
            RankedItem(
                title="Investment Fees",
                rank=2,
                value="28%",
                numeric_value=28.0,
                badge="SILVER",
                change="-1",
            ),
            RankedItem(
                title="Taxes & Churn",
                rank=3,
                value="18%",
                numeric_value=18.0,
                badge="BRONZE",
                change="NEW",
            ),
        ],
    )
    assert data.header_label == "TOP WEALTH DESTROYERS"
    assert data.variant == "dominance"
    assert data.footer_label == "Annual compounded drag over 20 years"
    assert len(data.items) == 3
    assert data.items[0].title == "Lifestyle Inflation"
    assert data.items[0].numeric_value == 42.0
    assert data.items[0].badge == "PRIMARY LEADER"


def test_ranked_list_backward_compatibility() -> None:
    data = RankedListData(
        items=[
            RankedItem(title="Item 1", value="100"),
            RankedItem(title="Item 2", value="50"),
        ]
    )
    assert len(data.items) == 2
    assert data.header_label is None
    assert data.variant is None
    assert data.footer_label is None
    assert data.show_bars is True


def test_ranked_list_registry_variants() -> None:
    defn = CompositionRegistry.get("ranked_list")
    assert defn is not None
    assert "dominance" in defn.allowed_variants
    assert "standard" in defn.allowed_variants
    assert "compact" in defn.allowed_variants


def test_ranked_list_resolver_mappings_2_3_5_items() -> None:
    resolver = CompositionResolver()

    # 5 items test
    five_items = [
        {"title": f"Asset {i}", "rank": i, "value": f"₹{10-i}L", "numeric_value": float(10-i)}
        for i in range(1, 6)
    ]
    spec = resolver.resolve_composition(
        composition_id="ranked_list",
        composition_data={
            "header_label": "TOP 5 ASSET CLASSES",
            "items": five_items,
            "variant": "dominance",
            "footer_label": "Indexed portfolio allocation",
        },
    )
    assert spec.props["headerLabel"] == "TOP 5 ASSET CLASSES"
    assert spec.props["variant"] == "dominance"
    assert spec.props["footerLabel"] == "Indexed portfolio allocation"
    assert spec.props["showBars"] is True
    assert len(spec.props["items"]) == 5
    assert spec.props["items"][0]["title"] == "Asset 1"
    assert spec.props["items"][0]["rank"] == 1
    assert spec.props["items"][0]["numericValue"] == 9.0


def test_ranked_list_planner_merge_preserves_new_fields() -> None:
    candidate = {
        "header_label": "LEADERBOARD",
        "variant": "dominance",
        "footer_label": "Summary of ranks",
        "items": [{"title": "Rank 1", "rank": 1}],
    }
    llm_result = {
        "items": [{"title": "Rank 1", "rank": 1, "value": "100"}],
    }
    intent = VisualIntent(
        intent_id="intent_ranked",
        narration_excerpt="Top wealth destroyers.",
        what_viewer_must_understand="Lifestyle inflation is the biggest drag on long-term wealth.",
        relationship_type="ranking",
    )
    merged = merge_factual_and_presentation_data("ranked_list", candidate, llm_result, intent)
    assert merged["header_label"] == "LEADERBOARD"
    assert merged["variant"] == "dominance"
    assert merged["footer_label"] == "Summary of ranks"

