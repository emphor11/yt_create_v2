from typing import Any
from domain.video_assembly_props import ComponentSpec

class ComponentResolver:
    def resolve_component(
        self,
        *,
        preferred_component: str,
        visual_goal: str,
        onscreen_text: str | None = None,
        component_data: dict[str, Any],
        narration_text: str,
    ) -> ComponentSpec:
        # Prioritize clean, viewer-facing onscreen_text over raw visual_goal camera directions
        display_headline = (onscreen_text or "").strip()
        if not display_headline:
            display_headline = (component_data.get("onscreen_text") or "").strip()
        if not display_headline:
            # Clean visual_goal if no explicit onscreen_text exists (fallback)
            display_headline = visual_goal

        right_raw = narration_text[:60] + "..." if len(narration_text) > 60 else narration_text

        # Generate clean, component-specific renderer props
        component_id_mapping = {
            "Stock Image": "StockImage",
            "Stock Video": "StockVideo",
            "Icon Animation": "IconAnimation",
        }
        if not preferred_component:
            # Smart fallback resolution based on visual_goal keywords
            instruction_lower = visual_goal.lower()
            if "compare" in instruction_lower or "comparison" in instruction_lower or "versus" in instruction_lower:
                component_id = "SplitComparison"
            elif "count" in instruction_lower or "number" in instruction_lower or "percent" in instruction_lower or "%" in instruction_lower:
                component_id = "NumberCounter"
            elif "chart" in instruction_lower or "graph" in instruction_lower:
                component_id = "Charts"
            elif "timeline" in instruction_lower or "step" in instruction_lower or "progression" in instruction_lower:
                component_id = "Timeline"
            elif "video" in instruction_lower or "clip" in instruction_lower or "footage" in instruction_lower:
                component_id = "StockVideo"
            elif "image" in instruction_lower or "photo" in instruction_lower:
                component_id = "StockImage"
            else:
                component_id = "Typography"
        else:
            component_id = component_id_mapping.get(preferred_component, preferred_component)

        if component_id == "SplitComparison":
            props = {
                "headerLabel": component_data.get("header_label") or "COMPARISON",
                "title": display_headline,
                "leftRole": component_data.get("left_role") or "Before",
                "leftLabel": component_data.get("left_label") or component_data.get("left_role") or "Before",
                "leftValue": component_data.get("left_value") if component_data.get("left_value") is not None else component_data.get("start_value", 0),
                "leftUnit": component_data.get("left_unit") or "",
                "rightRole": component_data.get("right_role") or "After",
                "rightLabel": component_data.get("right_label") or component_data.get("right_role") or "After",
                "rightValue": component_data.get("right_value") if component_data.get("right_value") is not None else component_data.get("end_value", 0),
                "rightUnit": component_data.get("right_unit") or "",
                "footerLabel": "",
            }
        elif component_id == "Typography":
            props = {
                "headerLabel": component_data.get("header_label") or "KEY INSIGHT",
                "text": display_headline,
                "subtitle": right_raw,
                "style": "headline",
                "footerLabel": "",
            }
        elif component_id == "NumberCounter":
            props = {
                "headerLabel": component_data.get("header_label") or "KEY METRIC",
                "title": display_headline,
                "startValue": component_data.get("start_value") if component_data.get("start_value") is not None else component_data.get("left_value", 0),
                "endValue": component_data.get("end_value") if component_data.get("end_value") is not None else component_data.get("right_value", 100),
                "label": component_data.get("label") or component_data.get("left_label") or "Metric",
                "unit": component_data.get("unit") or component_data.get("left_unit") or "",
                "footerLabel": "",
            }
        elif component_id == "Timeline":
            props = {
                "headerLabel": component_data.get("header_label") or "PROGRESSION",
                "title": display_headline,
                "steps": component_data.get("steps") or [display_headline, right_raw],
                "footerLabel": "",
            }
        elif component_id == "Charts":
            props = {
                "headerLabel": component_data.get("header_label") or "DATA BREAKDOWN",
                "title": display_headline,
                "chartType": component_data.get("chart_type") or "bar",
                "labels": component_data.get("labels") or component_data.get("x") or ["Before", "After"],
                "values": component_data.get("values") or component_data.get("y") or [component_data.get("start_value", 50), component_data.get("end_value", 100)],
                "unit": component_data.get("unit") or "",
                "x": component_data.get("labels") or component_data.get("x") or ["Before", "After"],
                "y": component_data.get("values") or component_data.get("y") or [component_data.get("start_value", 50), component_data.get("end_value", 100)],
                "footerLabel": "",
            }
        else:
            props = {
                "headerLabel": component_data.get("header_label") or (preferred_component.upper() if preferred_component else "VISUAL CONTEXT"),
                "text": display_headline,
                "subtitle": right_raw,
                "icon": component_data.get("icon") or "💡",
                "footerLabel": "",
            }

        return ComponentSpec(
            component_id=component_id,
            props=props
        )
