import re
from typing import Any, Literal
from pydantic import BaseModel, Field, ValidationError


# =====================================================================
# Strongly-Typed Polymorphic Component Data Models
# =====================================================================

class TypographyData(BaseModel):
    header_label: str | None = None
    text: str
    subtitle: str | None = None


class SplitComparisonData(BaseModel):
    header_label: str | None = None
    left_role: str
    left_label: str | None = None
    left_value: float | str
    left_unit: str | None = None
    right_role: str
    right_label: str | None = None
    right_value: float | str
    right_unit: str | None = None


class NumberCounterData(BaseModel):
    header_label: str | None = None
    label: str | None = None
    start_value: float = 0.0
    end_value: float
    unit: str | None = None


class ChartsData(BaseModel):
    header_label: str | None = None
    chart_type: Literal["bar", "line", "pie"] = "bar"
    labels: list[str] = Field(default_factory=list)
    values: list[float | int] = Field(default_factory=list)
    unit: str | None = None


class TimelineData(BaseModel):
    header_label: str | None = None
    steps: list[str] = Field(default_factory=list)


class IconAnimationData(BaseModel):
    header_label: str | None = None
    icon: str = "💡"
    label: str


class StockMediaData(BaseModel):
    pass


# =====================================================================
# Component Metadata & Registry
# =====================================================================

class ComponentDefinition(BaseModel):
    component: str
    data_model: type[BaseModel]
    required_roles: list[str] = Field(default_factory=list)
    supported_events: list[str] = Field(default_factory=list)
    constraints: dict[str, str] = Field(default_factory=dict)


class ComponentRegistry:
    CANONICAL_COMPONENTS = {
        "Typography": TypographyData,
        "SplitComparison": SplitComparisonData,
        "NumberCounter": NumberCounterData,
        "Charts": ChartsData,
        "Timeline": TimelineData,
        "IconAnimation": IconAnimationData,
        "StockVideo": StockMediaData,
        "StockImage": StockMediaData,
    }

    # Alias mapping for space-separated variants
    ALIASES = {
        "Stock Video": "StockVideo",
        "Stock Image": "StockImage",
        "Icon Animation": "IconAnimation",
    }

    def __init__(self) -> None:
        self._components: dict[str, ComponentDefinition] = {
            "Typography": ComponentDefinition(
                component="Typography",
                data_model=TypographyData,
                supported_events=["attention_shift"],
            ),
            "SplitComparison": ComponentDefinition(
                component="SplitComparison",
                data_model=SplitComparisonData,
                required_roles=["product_price", "monthly_payment"],
                supported_events=[
                    "reveal_full_price",
                    "reveal_monthly_payment",
                    "attention_shift",
                ],
                constraints={
                    "left_role": "product_price",
                    "right_role": "monthly_payment",
                },
            ),
            "NumberCounter": ComponentDefinition(
                component="NumberCounter",
                data_model=NumberCounterData,
                supported_events=["attention_shift"],
            ),
            "Charts": ComponentDefinition(
                component="Charts",
                data_model=ChartsData,
                supported_events=["attention_shift"],
            ),
            "Timeline": ComponentDefinition(
                component="Timeline",
                data_model=TimelineData,
                supported_events=["attention_shift"],
            ),
            "IconAnimation": ComponentDefinition(
                component="IconAnimation",
                data_model=IconAnimationData,
                supported_events=["attention_shift"],
            ),
            "StockVideo": ComponentDefinition(
                component="StockVideo",
                data_model=StockMediaData,
                supported_events=["attention_shift"],
            ),
            "StockImage": ComponentDefinition(
                component="StockImage",
                data_model=StockMediaData,
                supported_events=["attention_shift"],
            ),
        }
        # Add space-separated aliases to definitions
        for alias, canonical in self.ALIASES.items():
            self._components[alias] = self._components[canonical]

    @classmethod
    def canonical_name(cls, name: str) -> str:
        clean = name.strip() if name else ""
        return cls.ALIASES.get(clean, clean)

    @classmethod
    def is_supported(cls, name: str) -> bool:
        canonical = cls.canonical_name(name)
        return canonical in cls.CANONICAL_COMPONENTS

    @classmethod
    def get_data_model(cls, name: str) -> type[BaseModel] | None:
        canonical = cls.canonical_name(name)
        return cls.CANONICAL_COMPONENTS.get(canonical)

    def has_component(self, component: str) -> bool:
        return self.is_supported(component)

    def get_component(self, component: str) -> ComponentDefinition:
        canonical = self.canonical_name(component)
        return self._components[canonical]

    def available_components(self) -> set[str]:
        return set(self._components.keys())

    @classmethod
    def normalize_component_data(
        cls,
        preferred_component: str,
        raw_data: dict[str, Any] | None,
        visual_goal: str = "",
        narration_text: str = "",
    ) -> dict[str, Any]:
        """Self-healing normalization that repairs common LLM schema edge cases in place."""
        data = dict(raw_data) if isinstance(raw_data, dict) else {}
        canonical = cls.canonical_name(preferred_component)

        if canonical == "NumberCounter":
            if "start_value" not in data or data.get("start_value") is None:
                data["start_value"] = 0.0
            if "end_value" not in data or data.get("end_value") is None:
                # 1. Check if model provided target number in 'values' list
                if "values" in data and isinstance(data["values"], list) and len(data["values"]) > 0:
                    data["end_value"] = float(data["values"][0])
                else:
                    # 2. Extract numeric candidate from visual_goal, label, or narration
                    search_text = f"{visual_goal} {data.get('label', '')} {narration_text}"
                    candidates = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", search_text)
                    if candidates:
                        clean_num = float(candidates[-1].replace(",", "")) if len(candidates) > 1 and "%" not in candidates[-1] else float(candidates[0].replace(",", ""))
                        data["end_value"] = clean_num
                    else:
                        data["end_value"] = 100.0

        elif canonical == "Charts":
            if not data.get("chart_type"):
                data["chart_type"] = "bar"

        elif canonical == "Timeline":
            if ("steps" not in data or not data.get("steps")) and "labels" in data and isinstance(data["labels"], list):
                data["steps"] = data["labels"]

        elif canonical == "IconAnimation":
            if not data.get("icon"):
                data["icon"] = "⚠️" if ("warning" in visual_goal.lower() or "drag" in visual_goal.lower() or "multiplier" in visual_goal.lower()) else "💡"
            if not data.get("label"):
                data["label"] = data.get("header_label") or visual_goal or "Key Insight"

        elif canonical == "Typography":
            if not data.get("text"):
                data["text"] = data.get("header_label") or visual_goal or "Key Takeaway"

        elif canonical in ("StockVideo", "StockImage"):
            data = {}

        return data

    @classmethod
    def validate_component_data(
        cls,
        preferred_component: str,
        raw_data: dict[str, Any] | None,
        visual_goal: str = "",
        narration_text: str = "",
    ) -> tuple[bool, list[str], dict[str, Any]]:
        """Validates and normalizes component_data against its dedicated Pydantic model."""
        canonical = cls.canonical_name(preferred_component)
        model_cls = cls.get_data_model(canonical)
        if not model_cls:
            return False, [f"Unsupported component '{preferred_component}'."], {}

        normalized = cls.normalize_component_data(
            preferred_component, raw_data, visual_goal=visual_goal, narration_text=narration_text
        )

        try:
            model_cls.model_validate(normalized)
            return True, [], normalized
        except ValidationError as exc:
            errors = [f"{canonical} data validation error: {err['loc'][0]} - {err['msg']}" for err in exc.errors()]
            return False, errors, normalized

    @classmethod
    def get_polymorphic_beat_schema(cls, is_hook: bool = False) -> list[dict[str, Any]]:
        """Generates dynamic, polymorphic anyOf schemas for visual beats."""
        variants = []
        for canonical, model_cls in cls.CANONICAL_COMPONENTS.items():
            data_schema = model_cls.model_json_schema()
            data_schema.pop("title", None)
            
            beat_props: dict[str, Any] = {
                "beat_id": {"type": "string"},
                "preferred_component": {"type": "string", "enum": [canonical]},
                "visual_goal": {"type": "string"},
                "asset_query": {"type": "string"},
                "trigger_word": {"type": "string"},
                "component_data": data_schema,
            }
            if is_hook:
                beat_props["visual_instruction"] = {"type": "string"}

            variants.append({
                "type": "object",
                "properties": beat_props,
                "required": ["beat_id", "preferred_component", "visual_goal", "trigger_word", "component_data"],
            })
        return variants
