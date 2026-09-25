import pytest
from domain.visual_intent import VisualIntent, QuantitativeMeasurement, SemanticEntity
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
