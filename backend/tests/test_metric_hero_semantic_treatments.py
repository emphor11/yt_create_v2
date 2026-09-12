import pytest
from domain.visual_intent import VisualIntent, QuantitativeMeasurement, SemanticEntity
from engines.composition_planner_engine import (
    build_candidate_composition_data,
    merge_factual_and_presentation_data,
)
from engines.video_assembly.composition_resolver import CompositionResolver
from registries.composition_registry import CompositionRegistry, MetricHeroData


def test_metric_hero_data_accepts_new_variants():
    for var in ["hero_milestone", "supporting_metric", "warning_metric", "before_after_metric"]:
        data = MetricHeroData(
            value="₹50 lakh",
            label="Retirement Corpus",
            variant=var,
            polarity="negative" if var == "warning_metric" else "positive",
            direction="down" if var == "warning_metric" else "up",
            baseline_value="₹10 lakh" if var == "before_after_metric" else None,
            delta="+400%" if var == "before_after_metric" else None,
        )
        assert data.variant == var
        assert data.value == "₹50 lakh"


def test_build_candidate_composition_data_extracts_metric_hero_semantics():
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Purchasing power dropped to ₹26.",
        what_viewer_must_understand="Purchasing power drops to ₹26.",
        relationship_type="metric",
        measurements=[
            QuantitativeMeasurement(
                raw_value="₹26",
                metric_name="Ending Value",
                polarity="negative",
                direction="down",
                role="result",
            ),
            QuantitativeMeasurement(
                raw_value="₹100",
                metric_name="Initial Value",
                polarity="neutral",
                direction="flat",
                role="baseline",
            ),
            QuantitativeMeasurement(
                raw_value="-74%",
                polarity="negative",
                role="delta",
            ),
        ],
    )
    facts = build_candidate_composition_data("metric_hero", intent)
    assert facts["value"] == "₹26"
    assert facts["label"] == "Ending Value"
    assert facts["polarity"] == "negative"
    assert facts["direction"] == "down"
    assert facts["baseline_value"] == "₹100"
    assert facts["delta"] == "-74%"


def test_merge_preserves_metric_hero_semantics():
    candidate_facts = {
        "value": "₹26",
        "label": "Ending Value",
        "polarity": "negative",
        "direction": "down",
        "baseline_value": "₹100",
        "delta": "-74%",
    }
    llm_data = {
        "value": "something else",
        "label": "Custom Editorial Label",
        "variant": "warning_metric",
    }
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Purchasing power dropped to ₹26.",
        what_viewer_must_understand="Purchasing power drops to ₹26.",
        relationship_type="metric",
    )
    merged = merge_factual_and_presentation_data("metric_hero", candidate_facts, llm_data, intent)
    # Factual value is locked
    assert merged["value"] == "₹26"
    # Editorial label preserved
    assert merged["label"] == "Custom Editorial Label"
    # Semantics preserved
    assert merged["polarity"] == "negative"
    assert merged["direction"] == "down"
    assert merged["baseline_value"] == "₹100"
    assert merged["delta"] == "-74%"
    assert merged["variant"] == "warning_metric"


def test_composition_resolver_maps_metric_hero_semantic_props():
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="metric_hero",
        composition_data={
            "value": "₹1.2 Cr",
            "label": "Retirement Target",
            "context": "15 Years",
            "variant": "before_after_metric",
            "polarity": "positive",
            "direction": "up",
            "baseline_value": "₹50,000",
            "delta": "+24x Growth",
        },
        variant="before_after_metric",
    )
    assert spec.component_id == "MetricHero"
    props = spec.props
    assert props["value"] == "₹1.2 Cr"
    assert props["variant"] == "before_after_metric"
    assert props["polarity"] == "positive"
    assert props["direction"] == "up"
    assert props["baselineValue"] == "₹50,000"
    assert props["delta"] == "+24x Growth"
