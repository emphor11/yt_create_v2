"""
CompositionResolver — maps a CompositionBeat into a Remotion-ready ComponentSpec.

Translates snake_case composition_data into camelCase TypeScript props
matching the component interfaces defined in renderer/remotion/src/types.ts.
Provides graceful fallbacks if validation or lookup fails.
"""
from __future__ import annotations

from typing import Any

from domain.video_assembly_props import ComponentSpec
from registries.composition_registry import CompositionRegistry


class CompositionResolver:
    """
    Resolves a visual composition into a Remotion ComponentSpec with camelCase props.
    """

    def resolve_composition(
        self,
        *,
        composition_id: str,
        composition_data: dict[str, Any],
        variant: str | None = None,
        visual_goal: str = "",
        narration_text: str = "",
    ) -> ComponentSpec:
        """
        Translates a composition definition and its data into a ComponentSpec.
        """
        if not composition_id or not composition_id.strip():
            return self._fallback_component(visual_goal or narration_text)

        defn = CompositionRegistry.get(composition_id)
        if defn is None:
            return self._fallback_component(visual_goal or narration_text)

        # Validate / normalize composition data
        is_valid, errors, data = CompositionRegistry.validate_composition_data(
            composition_id=composition_id,
            raw_data=composition_data,
            visual_goal=visual_goal,
        )

        if not is_valid:
            # Degrade gracefully to fallback component
            return self._fallback_component(visual_goal or narration_text)

        cid = defn.composition_id

        if cid == "metric_hero":
            props = {
                "value": data.get("value", ""),
                "label": data.get("label", ""),
                "context": data.get("context"),
                "emphasis": data.get("emphasis"),
                "variant": variant or data.get("emphasis") or "hero",
            }

        elif cid == "calculation_story":
            props = {
                "inputLabel": data.get("input_label", ""),
                "inputValue": data.get("input_value", ""),
                "operationLabel": data.get("operation_label", "×"),
                "rateLabel": data.get("rate_label", ""),
                "resultLabel": data.get("result_label", ""),
                "resultValue": data.get("result_value", ""),
                "note": data.get("note"),
            }

        elif cid == "cause_effect":
            causes_raw = data.get("causes", [])
            causes_props = [
                {
                    "label": c.get("label", "") if isinstance(c, dict) else getattr(c, "label", ""),
                    "value": c.get("value") if isinstance(c, dict) else getattr(c, "value", None),
                    "icon": c.get("icon") if isinstance(c, dict) else getattr(c, "icon", None),
                }
                for c in causes_raw
            ]
            props = {
                "causes": causes_props,
                "connector": data.get("connector", "leads to"),
                "outcomeLabel": data.get("outcome_label", ""),
                "outcomeValue": data.get("outcome_value"),
                "outcomeSeverity": data.get("outcome_severity", "neutral"),
            }

        elif cid == "time_decay":
            props = {
                "fixedAmount": data.get("fixed_amount", ""),
                "amountLabel": data.get("amount_label", ""),
                "timePeriod": data.get("time_period", ""),
                "emphasis": data.get("emphasis", "purchasing_power_decline"),
                "annotation": data.get("annotation"),
                "showChart": data.get("show_chart", True),
            }

        elif cid == "multi_factor_pressure":
            factors_raw = data.get("factors", [])
            factors_props = [
                {
                    "label": f.get("label", "") if isinstance(f, dict) else getattr(f, "label", ""),
                    "value": f.get("value") if isinstance(f, dict) else getattr(f, "value", None),
                    "severity": f.get("severity") if isinstance(f, dict) else getattr(f, "severity", None),
                }
                for f in factors_raw
            ]
            props = {
                "factors": factors_props,
                "combinedLabel": data.get("combined_label", ""),
                "combinedSeverity": data.get("combined_severity", "critical"),
                "outcomeNote": data.get("outcome_note"),
            }

        elif cid == "comparison_split":
            props = {
                "headerLabel": data.get("comparison_label"),
                "comparisonLabel": data.get("comparison_label"),
                "variant": variant or data.get("variant") or "cards",
                "tone": data.get("tone") or "neutral",
                "leftRole": data.get("left_role", ""),
                "leftLabel": data.get("left_label"),
                "leftValue": data.get("left_value", ""),
                "leftUnit": data.get("left_unit"),
                "rightRole": data.get("right_role", ""),
                "rightLabel": data.get("right_label"),
                "rightValue": data.get("right_value", ""),
                "rightUnit": data.get("right_unit"),
                "delta": data.get("delta"),
                "winner": data.get("winner"),
            }

        elif cid == "ranked_list":
            items_raw = data.get("items", [])
            mapped_items = [
                {
                    "title": item.get("title", "") if isinstance(item, dict) else getattr(item, "title", ""),
                    "rank": item.get("rank") if isinstance(item, dict) else getattr(item, "rank", None),
                    "subtitle": item.get("subtitle") if isinstance(item, dict) else getattr(item, "subtitle", None),
                    "value": item.get("value") if isinstance(item, dict) else getattr(item, "value", None),
                    "numericValue": item.get("numeric_value") if isinstance(item, dict) else getattr(item, "numeric_value", None),
                    "badge": item.get("badge") if isinstance(item, dict) else getattr(item, "badge", None),
                }
                for item in items_raw
            ]
            props = {
                "headerLabel": data.get("header_label", ""),
                "showBars": data.get("show_bars", True),
                "items": mapped_items,
            }

        elif cid == "process_flow":
            steps_raw = data.get("steps", [])
            mapped_steps = [
                {
                    "title": s.get("title", "") if isinstance(s, dict) else getattr(s, "title", ""),
                    "subtitle": s.get("subtitle") if isinstance(s, dict) else getattr(s, "subtitle", None),
                    "type": s.get("type", "step") if isinstance(s, dict) else getattr(s, "type", "step"),
                    "value": s.get("value") if isinstance(s, dict) else getattr(s, "value", None),
                    "connectorLabel": s.get("connector_label") if isinstance(s, dict) else getattr(s, "connector_label", None),
                }
                for s in steps_raw
            ]
            props = {
                "headerLabel": data.get("header_label", ""),
                "layout": variant or data.get("layout") or "auto",
                "steps": mapped_steps,
            }

        elif cid == "broll_caption":
            props = {
                "caption": data.get("caption", visual_goal or narration_text),
                "emphasisPhrase": data.get("emphasis_phrase"),
                "author": data.get("author"),
            }

        else:
            return self._fallback_component(visual_goal or narration_text)

        return ComponentSpec(
            component_id=defn.remotion_component_id,
            props=props,
        )

    def _fallback_component(self, text: str) -> ComponentSpec:
        """Safe fallback to standard Typography statement."""
        return ComponentSpec(
            component_id="Typography",
            props={
                "text": text or "Important Insight",
                "variant": "statement",
            },
        )
