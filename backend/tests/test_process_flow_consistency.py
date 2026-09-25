from typing import Any
import pytest
from registries.composition_registry import CompositionRegistry, ProcessFlowData, ProcessStepItem
from engines.composition_planner_engine import (
    build_candidate_composition_data,
    merge_factual_and_presentation_data,
)
from engines.video_assembly.composition_resolver import CompositionResolver
from domain.visual_intent import VisualIntent, SemanticEntity


def test_process_flow_data_accepts_all_fields() -> None:
    data = ProcessFlowData(
        header_label="WEALTH ACCUMULATION SYSTEM",
        layout="horizontal",
        variant="horizontal",
        footer_label="Step-by-step automated wealth engine",
        steps=[
            ProcessStepItem(
                title="Earn Active Income",
                subtitle="Salary & Freelancing",
                type="cause",
                value="₹2,00,000/mo",
                connector_label="auto-debits",
            ),
            ProcessStepItem(
                title="Systematic Investment",
                subtitle="Index Funds + PPF",
                type="step",
                value="₹75,000/mo",
                connector_label="compounds into",
            ),
            ProcessStepItem(
                title="Corpus Compounding",
                subtitle="Long-Term Wealth",
                type="outcome",
                value="₹5.2 Crore",
            ),
        ],
    )
    assert data.header_label == "WEALTH ACCUMULATION SYSTEM"
    assert data.layout == "horizontal"
    assert data.variant == "horizontal"
    assert data.footer_label == "Step-by-step automated wealth engine"
    assert len(data.steps) == 3
    assert data.steps[0].type == "cause"
    assert data.steps[2].type == "outcome"


def test_process_flow_backward_compatibility() -> None:
    data = ProcessFlowData(
        steps=[
            ProcessStepItem(title="Step 1"),
            ProcessStepItem(title="Step 2"),
        ]
    )
    assert len(data.steps) == 2
    assert data.header_label is None
    assert data.layout == "auto"
    assert data.variant is None
    assert data.footer_label is None


def test_process_flow_registry_variants() -> None:
    defn = CompositionRegistry.get("process_flow")
    assert defn is not None
    assert "horizontal" in defn.allowed_variants
    assert "vertical" in defn.allowed_variants
    assert "auto" in defn.allowed_variants


def test_process_flow_resolver_mappings_2_3_5_steps() -> None:
    resolver = CompositionResolver()

    # 5 steps vertical test
    five_steps = [
        {
            "title": f"Step {i}",
            "subtitle": f"Phase {i} Execution",
            "type": "cause" if i == 1 else "outcome" if i == 5 else "step",
            "value": f"Stage {i}",
            "connector_label": "then" if i < 5 else None,
        }
        for i in range(1, 6)
    ]

    spec = resolver.resolve_composition(
        composition_id="process_flow",
        composition_data={
            "header_label": "DEBT SNOWBALL METHOD",
            "layout": "vertical",
            "variant": "vertical",
            "steps": five_steps,
            "footer_label": "Guaranteed debt-free timeline",
        },
    )
    assert spec.props["headerLabel"] == "DEBT SNOWBALL METHOD"
    assert spec.props["layout"] == "vertical"
    assert spec.props["variant"] == "vertical"
    assert spec.props["footerLabel"] == "Guaranteed debt-free timeline"
    assert len(spec.props["steps"]) == 5
    assert spec.props["steps"][0]["type"] == "cause"
    assert spec.props["steps"][4]["type"] == "outcome"
    assert spec.props["steps"][0]["connectorLabel"] == "then"


def test_process_flow_planner_merge_preserves_new_fields() -> None:
    candidate = {
        "header_label": "AUTOMATION PIPELINE",
        "layout": "horizontal",
        "variant": "horizontal",
        "footer_label": "Zero manual overhead",
        "steps": [{"title": "Step 1"}],
    }
    llm_result = {
        "steps": [{"title": "Step 1", "value": "100"}],
    }
    intent = VisualIntent(
        intent_id="intent_process",
        narration_excerpt="Wealth accumulation system.",
        what_viewer_must_understand="Following the process flow produces automated long-term wealth.",
        relationship_type="process",
        entities=[
            SemanticEntity(name="Step 1", role="step"),
            SemanticEntity(name="Step 2", role="step"),
        ],
    )
    merged = merge_factual_and_presentation_data("process_flow", candidate, llm_result, intent)
    assert merged["header_label"] == "AUTOMATION PIPELINE"
    assert merged["layout"] == "horizontal"
    assert merged["variant"] == "horizontal"
    assert merged["footer_label"] == "Zero manual overhead"

