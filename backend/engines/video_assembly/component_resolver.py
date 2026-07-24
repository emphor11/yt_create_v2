from typing import Any
from domain.video_assembly_props import ComponentSpec

class ComponentResolver:
    def resolve_component(
        self,
        *,
        preferred_component: str,
        visual_goal: str,
        component_data: dict[str, Any],
        narration_text: str,
    ) -> ComponentSpec:
        # Keep ComponentSpec.props limited to rendering-specific data only
        # We transform the data into a standard left/right structure that aligns with visual layouts
        left_label = "Visual Beat"
        left_raw = visual_goal
        right_label = "Context"
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
                "leftLabel": component_data.get("left_label", "Before"),
                "leftValue": component_data.get("left_value", 0),
                "rightLabel": component_data.get("right_label", "After"),
                "rightValue": component_data.get("right_value", 0)
            }
        elif component_id == "Typography":
            props = {
                "text": visual_goal,
                "subtitle": right_raw,
                "style": "headline"
            }
        elif component_id == "NumberCounter":
            props = {
                "startValue": component_data.get("left_value", 0),
                "endValue": component_data.get("right_value", 100),
                "label": component_data.get("left_label", "Metric")
            }
        elif component_id == "Timeline":
            props = {
                "steps": [visual_goal, right_raw]
            }
        elif component_id == "Charts":
            props = {
                "x": ["Income", "Expenses", "Savings"],
                "y": [component_data.get("left_value", 5000), component_data.get("right_value", 4800), 200]
            }
        else:
            props = {
                "text": visual_goal,
                "subtitle": right_raw
            }

        return ComponentSpec(
            component_id=component_id,
            props=props
        )
