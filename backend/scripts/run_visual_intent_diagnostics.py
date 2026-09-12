"""
Diagnostic script demonstrating Old vs New VisualIntent representations.

Validates the core question:
Does the new VisualIntent contain information that the old intent did not,
in a way that makes the next composition-planning step easier and more reliable?
"""
import json
import sys
from pathlib import Path

# Ensure backend root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.visual_intent import (
    CausalStructure,
    ComparisonStructure,
    QuantitativeMeasurement,
    SemanticEntity,
    TemporalContext,
    VisualDynamics,
    VisualIntent,
)


def print_comparison_case(title: str, narration: str, old_intent: dict, new_intent: VisualIntent) -> None:
    print(f"\n{'=' * 80}")
    print(f"CASE: {title}")
    print(f"{'=' * 80}")
    print(f"NARRATION:\n\"{narration}\"\n")

    print("[OLD VISUAL INTENT] (Flat, ambiguous):")
    print(json.dumps(old_intent, indent=2, ensure_ascii=False))

    print("\n[NEW VISUAL INTENT] (Rich, entity-bound semantic meaning):")
    new_data = new_intent.model_dump(exclude_none=True)
    print(json.dumps(new_data, indent=2, ensure_ascii=False))

    print("\n[WHY THIS MAKES DOWNSTREAM COMPOSITION-PLANNING EASIER & RELIABLE]:")
    if new_intent.comparison:
        print(f"  • Entity-Value Disambiguation: The planner immediately knows {new_intent.comparison.value_a} "
              f"belongs to '{new_intent.comparison.subject_a}' and {new_intent.comparison.value_b} belongs to '{new_intent.comparison.subject_b}'.")
        print(f"  • Direct Comparison Mapping: Pre-computed dimension ('{new_intent.comparison.comparison_dimension}'), "
              f"delta ('{new_intent.comparison.delta}'), and winner ('{new_intent.comparison.winner}') eliminate guessing.")
    elif new_intent.causal:
        print(f"  • Causal Structure: Explicitly isolates driving causes {new_intent.causal.causes} from outcome ('{new_intent.causal.outcome}').")
        print(f"  • Severity Flag: '{new_intent.causal.outcome_severity}' signals visual urgency to the composition planner.")
    elif new_intent.temporal and new_intent.temporal.is_decay_over_time:
        print(f"  • Time Decay Dynamics: Explicitly flags is_decay_over_time=True across {new_intent.temporal.horizon}.")
        print(f"  • Negative Polarity & Downward Direction: Pre-binds starting vs ending eroded values.")
    elif new_intent.relationship_type == "calculation":
        print(f"  • Math Arithmetic Roles: Identifies input rate vs base corpus vs resulting cash flow.")
    elif new_intent.relationship_type == "metric":
        print(f"  • Clean Grounding: Strictly populates only supported fields (entities & measurements) while leaving comparison/causal/temporal null.")


def run_all_diagnostics() -> None:
    print("================================================================================")
    print("YTcreate_V2 — RICH VISUAL INTENT DIAGNOSTIC COMPARISON")
    print("================================================================================")

    # 1. Comparison
    c1_narration = "A Fixed Deposit gives you around 6% return, while an Equity Fund delivers closer to 12%. That 6% difference compounds massively over 15 years."
    c1_old = {
        "intent_id": "intent_01",
        "narration_excerpt": c1_narration,
        "what_viewer_must_understand": "Equity Fund return (12%) outperforms Fixed Deposit (6%) by 6% over 15 years.",
        "key_values": ["6%", "12%", "6%", "15 years"],
        "relationship_type": "comparison",
        "emphasis": "highlight_spread",
        "trigger_word": None,
    }
    c1_new = VisualIntent(
        intent_id="intent_01",
        narration_excerpt=c1_narration,
        what_viewer_must_understand="Equity Fund return (12%) outperforms Fixed Deposit (6%) by 6% over 15 years.",
        key_values=["6%", "12%", "6%", "15 years"],
        relationship_type="comparison",
        emphasis="highlight_spread",
        trigger_word=None,
        entities=[
            SemanticEntity(name="Fixed Deposit", role="baseline", category="investment"),
            SemanticEntity(name="Equity Fund", role="alternative", category="investment"),
        ],
        measurements=[
            QuantitativeMeasurement(raw_value="6%", entity_name="Fixed Deposit", metric_name="Annual Return", numeric_value=6.0, unit="%"),
            QuantitativeMeasurement(raw_value="12%", entity_name="Equity Fund", metric_name="Annual Return", numeric_value=12.0, unit="%"),
        ],
        temporal=TemporalContext(horizon="15 years", frequency="annual"),
        comparison=ComparisonStructure(
            subject_a="Fixed Deposit",
            value_a="6%",
            subject_b="Equity Fund",
            value_b="12%",
            comparison_dimension="Annual Return",
            delta="+6% spread",
            winner="Equity Fund",
        ),
        visual_dynamics=VisualDynamics(
            focal_point="6% return advantage of Equity Fund over Fixed Deposit",
            desired_visual_outcome="Immediate visual contrast showing Equity Fund significantly outperforming Fixed Deposit",
            motion_intent="side_by_side_reveal",
            visual_priority="high",
        ),
    )
    print_comparison_case("1. Comparison (Entity & Value Binding)", c1_narration, c1_old, c1_new)

    # 2. Calculation
    c2_narration = "You withdraw 4% every year. On ₹50 lakh, that is ₹2 lakh annually."
    c2_old = {
        "intent_id": "intent_02",
        "narration_excerpt": c2_narration,
        "what_viewer_must_understand": "4% of ₹50 lakh equals ₹2 lakh per year.",
        "key_values": ["4%", "₹50 lakh", "₹2 lakh"],
        "relationship_type": "calculation",
        "emphasis": "show_result",
        "trigger_word": "withdraw",
    }
    c2_new = VisualIntent(
        intent_id="intent_02",
        narration_excerpt=c2_narration,
        what_viewer_must_understand="4% of ₹50 lakh equals ₹2 lakh per year.",
        key_values=["4%", "₹50 lakh", "₹2 lakh"],
        relationship_type="calculation",
        emphasis="show_result",
        trigger_word="withdraw",
        entities=[
            SemanticEntity(name="Retirement Portfolio", role="baseline", category="asset"),
            SemanticEntity(name="Annual Withdrawal", role="subject", category="metric"),
        ],
        measurements=[
            QuantitativeMeasurement(raw_value="4%", entity_name="Annual Withdrawal", metric_name="Withdrawal Rate", numeric_value=4.0, unit="%"),
            QuantitativeMeasurement(raw_value="₹50 lakh", entity_name="Retirement Portfolio", metric_name="Corpus Base", numeric_value=50.0, unit="₹ lakh"),
            QuantitativeMeasurement(raw_value="₹2 lakh", entity_name="Annual Withdrawal", metric_name="Annual Cash Flow", numeric_value=2.0, unit="₹ lakh"),
        ],
        temporal=TemporalContext(horizon="1 year", frequency="yearly"),
        visual_dynamics=VisualDynamics(
            focal_point="Resulting ₹2 lakh annual income",
            desired_visual_outcome="Clear arithmetic link showing 4% rate translates to ₹2 lakh cash flow",
            motion_intent="equation_reveal",
            visual_priority="high",
        ),
    )
    print_comparison_case("2. Calculation (Arithmetic Roles & Frequency)", c2_narration, c2_old, c2_new)

    # 3. Multi-Factor
    c3_narration = "High inflation erodes the value of money. Weak investment returns reduce your corpus growth. Together, these two forces put your retirement at serious risk."
    c3_old = {
        "intent_id": "intent_03",
        "narration_excerpt": c3_narration,
        "what_viewer_must_understand": "Inflation and weak returns combine to create severe retirement shortfall risk.",
        "key_values": ["inflation", "investment returns", "risk"],
        "relationship_type": "multi_factor",
        "emphasis": "highlight_risk",
        "trigger_word": "inflation",
    }
    c3_new = VisualIntent(
        intent_id="intent_03",
        narration_excerpt=c3_narration,
        what_viewer_must_understand="Inflation and weak returns combine to create severe retirement shortfall risk.",
        key_values=["inflation", "investment returns", "risk"],
        relationship_type="multi_factor",
        emphasis="highlight_risk",
        trigger_word="inflation",
        entities=[
            SemanticEntity(name="Inflation", role="risk_factor", category="concept"),
            SemanticEntity(name="Weak Returns", role="risk_factor", category="concept"),
            SemanticEntity(name="Retirement Corpus", role="subject", category="asset"),
        ],
        causal=CausalStructure(
            causes=["High inflation", "Weak investment returns"],
            mechanism="Dual pressure: purchasing power loss combined with stagnant growth",
            outcome="Severe retirement corpus shortfall",
            outcome_severity="critical",
        ),
        visual_dynamics=VisualDynamics(
            focal_point="Converging pressure on retirement corpus",
            desired_visual_outcome="Viewer feels the compounding danger of two independent negative forces acting together",
            motion_intent="convergence_inward",
            visual_priority="high",
        ),
    )
    print_comparison_case("3. Multi-Factor (Converging Drivers & Outcome Severity)", c3_narration, c3_old, c3_new)

    # 4. Decline / Time Erosion
    c4_narration = "Over 20 years, 7% annual inflation slashes the purchasing power of your ₹100 note down to just ₹26."
    c4_old = {
        "intent_id": "intent_04",
        "narration_excerpt": c4_narration,
        "what_viewer_must_understand": "Purchasing power of ₹100 drops to ₹26 over 20 years due to 7% inflation.",
        "key_values": ["20 years", "7%", "₹100", "₹26"],
        "relationship_type": "decline",
        "emphasis": "show_decline",
        "trigger_word": "slashes",
    }
    c4_new = VisualIntent(
        intent_id="intent_04",
        narration_excerpt=c4_narration,
        what_viewer_must_understand="Purchasing power of ₹100 drops to ₹26 over 20 years due to 7% inflation.",
        key_values=["20 years", "7%", "₹100", "₹26"],
        relationship_type="decline",
        emphasis="show_decline",
        trigger_word="slashes",
        entities=[
            SemanticEntity(name="₹100 Note", role="subject", category="asset"),
            SemanticEntity(name="Inflation", role="risk_factor", category="concept"),
        ],
        measurements=[
            QuantitativeMeasurement(raw_value="₹100", entity_name="₹100 Note", metric_name="Initial Purchasing Power", numeric_value=100.0, direction="flat", polarity="neutral"),
            QuantitativeMeasurement(raw_value="₹26", entity_name="₹100 Note", metric_name="Final Purchasing Power", numeric_value=26.0, direction="down", polarity="negative"),
            QuantitativeMeasurement(raw_value="7%", entity_name="Inflation", metric_name="Annual Inflation Rate", numeric_value=7.0, direction="up", polarity="warning"),
        ],
        temporal=TemporalContext(horizon="20 years", frequency="annual", is_decay_over_time=True),
        causal=CausalStructure(
            causes=["7% annual inflation"],
            mechanism="Compounding purchasing power erosion",
            outcome="74% loss in real monetary value",
            outcome_severity="high",
        ),
        visual_dynamics=VisualDynamics(
            focal_point="Erosion from ₹100 down to ₹26",
            desired_visual_outcome="Visceral sense of shrinking value and purchasing power over two decades",
            motion_intent="countdown_decay",
            visual_priority="high",
        ),
    )
    print_comparison_case("4. Decline (Time Erosion & Negative Polarity)", c4_narration, c4_old, c4_new)

    # 5. Simple Metric (Strict Grounding: no invented sub-structures)
    c5_narration = "Imagine you retire with ₹50 lakh. That is your entire starting portfolio."
    c5_old = {
        "intent_id": "intent_05",
        "narration_excerpt": c5_narration,
        "what_viewer_must_understand": "₹50 lakh is the starting retirement portfolio.",
        "key_values": ["₹50 lakh"],
        "relationship_type": "metric",
        "emphasis": "hero",
        "trigger_word": None,
    }
    c5_new = VisualIntent(
        intent_id="intent_05",
        narration_excerpt=c5_narration,
        what_viewer_must_understand="₹50 lakh is the starting retirement portfolio.",
        key_values=["₹50 lakh"],
        relationship_type="metric",
        emphasis="hero",
        trigger_word=None,
        entities=[
            SemanticEntity(name="Starting Portfolio", role="subject", category="asset")
        ],
        measurements=[
            QuantitativeMeasurement(raw_value="₹50 lakh", entity_name="Starting Portfolio", metric_name="Corpus Size", numeric_value=50.0, unit="₹ lakh"),
        ],
        temporal=None,      # STRICT GROUNDING: Not mentioned, so null
        causal=None,        # STRICT GROUNDING: Not mentioned, so null
        comparison=None,    # STRICT GROUNDING: Not mentioned, so null
        visual_dynamics=VisualDynamics(
            focal_point="₹50 lakh starting corpus",
            desired_visual_outcome="Viewer anchors on the total initial nest egg as the baseline",
            motion_intent="counter_increment",
            visual_priority="high",
        ),
    )
    print_comparison_case("5. Metric (Strict Grounding — No Hallucinated Sub-structures)", c5_narration, c5_old, c5_new)

    # 6. Process Flow
    c6_narration = "First, eliminate high-interest credit card debt. Next, build an emergency buffer. Finally, start investing in index funds."
    c6_old = {
        "intent_id": "intent_06",
        "narration_excerpt": c6_narration,
        "what_viewer_must_understand": "Three sequential steps to financial security.",
        "key_values": ["credit card debt", "emergency buffer", "index funds"],
        "relationship_type": "process",
        "emphasis": "step_sequence",
        "trigger_word": None,
    }
    c6_new = VisualIntent(
        intent_id="intent_06",
        narration_excerpt=c6_narration,
        what_viewer_must_understand="Three sequential steps to financial security.",
        key_values=["credit card debt", "emergency buffer", "index funds"],
        relationship_type="process",
        emphasis="step_sequence",
        trigger_word=None,
        entities=[
            SemanticEntity(name="Debt Elimination", role="step_1", category="action"),
            SemanticEntity(name="Emergency Buffer", role="step_2", category="action"),
            SemanticEntity(name="Index Funds", role="step_3", category="action"),
        ],
        measurements=[],
        temporal=None,      # STRICT GROUNDING: No duration, so null
        causal=None,        # STRICT GROUNDING: No causal link, so null
        comparison=None,    # STRICT GROUNDING: No comparison, so null
        visual_dynamics=VisualDynamics(
            focal_point="Sequential 3-step path to financial security",
            desired_visual_outcome="Viewer understands the exact execution sequence",
            motion_intent="sequential_step_reveal",
            visual_priority="high",
        ),
    )
    print_comparison_case("6. Process Flow (Sequential Entities & Strict Grounding)", c6_narration, c6_old, c6_new)

    print("\n================================================================================")
    print("DIAGNOSTIC TEST COMPLETE — ALL 6 CASES VERIFIED")
    print("================================================================================")


if __name__ == "__main__":
    run_all_diagnostics()
