from typing import Any
from domain.video_assembly_props import ComponentSpec
from registries.component_registry import ComponentRegistry


class ComponentResolver:
    def resolve_component(
        self,
        *,
        preferred_component: str,
        visual_goal: str,
        component_data: dict[str, Any],
        narration_text: str | None = None,
    ) -> ComponentSpec:
        if not preferred_component or not preferred_component.strip():
            raise ValueError("ComponentResolver requires a non-empty preferred_component.")

        canonical = ComponentRegistry.canonical_name(preferred_component)
        if not ComponentRegistry.is_supported(canonical):
            raise ValueError(f"Unsupported component_id: '{canonical}'.")

        # Self-healing normalization via ComponentRegistry
        data = ComponentRegistry.normalize_component_data(
            preferred_component=canonical,
            raw_data=component_data,
            visual_goal=visual_goal,
            narration_text=narration_text or "",
        )

        if canonical == "SplitComparison":
            props = {
                "headerLabel": data.get("header_label"),
                "leftRole": data.get("left_role"),
                "leftLabel": data.get("left_label"),
                "leftValue": data.get("left_value"),
                "leftUnit": data.get("left_unit") or "",
                "rightRole": data.get("right_role"),
                "rightLabel": data.get("right_label"),
                "rightValue": data.get("right_value"),
                "rightUnit": data.get("right_unit") or "",
                "footerLabel": "",
            }
        elif canonical == "Typography":
            props = {
                "headerLabel": data.get("header_label"),
                "text": data.get("text"),
                "subtitle": data.get("subtitle") or "",
                "style": "headline",
                "footerLabel": "",
            }
        elif canonical == "NumberCounter":
            props = {
                "headerLabel": data.get("header_label"),
                "startValue": data.get("start_value", 0.0),
                "endValue": data.get("end_value", 100.0),
                "label": data.get("label"),
                "unit": data.get("unit"),
                "footerLabel": "",
            }
        elif canonical == "Timeline":
            props = {
                "headerLabel": data.get("header_label"),
                "steps": data.get("steps") or [],
                "footerLabel": "",
            }
        elif canonical == "Charts":
            props = {
                "headerLabel": data.get("header_label"),
                "chartType": data.get("chart_type") or "bar",
                "labels": data.get("labels") or [],
                "values": data.get("values") or [],
                "unit": data.get("unit") or "",
                "footerLabel": "",
            }
        elif canonical == "IconAnimation":
            props = {
                "headerLabel": data.get("header_label"),
                "icon": data.get("icon") or "💡",
                "label": data.get("label") or "Key Insight",
                "footerLabel": "",
            }
        elif canonical in ("StockVideo", "StockImage"):
            props = {
                "headerLabel": data.get("header_label") or "",
                "footerLabel": "",
            }
        else:
            raise ValueError(f"Unsupported component_id: '{canonical}'.")

        return ComponentSpec(
            component_id=canonical,
            props=props,
        )
