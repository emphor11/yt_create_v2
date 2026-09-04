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
    variant: str | None = None  # "headline" | "question" | "statement" | "takeaway" | "metric" | "quote"
    highlight: str | None = None
    align: str | None = None    # "left" | "center"
    value: float | int | str | None = None
    author: str | None = None


class SplitComparisonData(BaseModel):
    header_label: str | None = None
    comparison_label: str | None = None  # e.g., "MARKET CAP", "REVENUE"
    variant: str | None = None            # "cards" | "versus" | "metric_compare"
    tone: str | None = None               # "neutral" | "positive_negative" | "before_after"
    left_role: str
    left_label: str | None = None
    left_value: float | str
    left_unit: str | None = None
    right_role: str
    right_label: str | None = None
    right_value: float | str
    right_unit: str | None = None
    delta: str | None = None              # e.g., "+8.6%", "+$300B"
    winner: str | None = None             # "left" | "right"


class NumberCounterData(BaseModel):
    header_label: str | None = None
    variant: str | None = None  # "single" | "change"
    label: str | None = None
    start_value: float | int | None = 0
    end_value: float | int
    prefix: str | None = None   # "$", "₹", "€"
    suffix: str | None = None   # "B", "M", "%", "years"
    unit: str | None = None     # backward compatibility
    precision: int | None = None
    delta: str | None = None    # e.g., "+66.7%", "+$400B"
    subtitle: str | None = None


class ChartsData(BaseModel):
    header_label: str | None = None
    chart_type: Literal["bar", "line", "pie", "donut", "horizontal_bar"] = "bar"
    labels: list[str] = Field(default_factory=list)
    values: list[float | int] = Field(default_factory=list)
    unit: str | None = None
    highlight_index: int | None = None
    highlight_label: str | None = None
    annotation: str | None = None
    center_label: str | None = None
    center_value: str | None = None


class TimelineEventData(BaseModel):
    date: str
    title: str
    subtitle: str | None = None
    value: float | int | str | None = None
    type: str | None = None  # "normal" | "major" | "warning" | "positive"
    icon: str | None = None


class TimelineData(BaseModel):
    header_label: str | None = None
    variant: str | None = None  # "milestone" | "detailed"
    events: list[TimelineEventData] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)


class ProcessStepData(BaseModel):
    title: str
    subtitle: str | None = None
    type: str | None = None  # "cause", "step", "outcome"
    value: float | int | str | None = None
    connector_label: str | None = None  # e.g., "increases", "reduces", "triggers"
    icon: str | None = None


class ProcessFlowData(BaseModel):
    header_label: str | None = None
    layout: str | None = None  # "horizontal" | "vertical" | "auto"
    steps: list[ProcessStepData] = Field(default_factory=list)


class KPICardData(BaseModel):
    label: str
    value: float | int | str
    unit: str | None = None
    trend: str | None = None
    subtitle: str | None = None
    icon: str | None = None
    is_primary: bool | None = False


class KPIGridData(BaseModel):
    header_label: str | None = None
    featured_index: int | None = 0
    kpis: list[KPICardData] = Field(default_factory=list)


class ProgressiveListItemData(BaseModel):
    title: str | None = None
    text: str | None = None
    subtitle: str | None = None
    icon: str | None = None
    highlight: bool | None = False
    value: float | int | str | None = None


class ProgressiveListData(BaseModel):
    header_label: str | None = None
    variant: str | None = None  # "detailed" | "compact"
    items: list[ProgressiveListItemData] = Field(default_factory=list)


class RankedListItemData(BaseModel):
    title: str
    rank: int | str | None = None
    subtitle: str | None = None
    value: float | int | str | None = None
    numeric_value: float | int | None = None
    badge: str | None = None
    change: str | None = None  # e.g., "+2", "-1", "NEW"
    logo: str | None = None
    icon: str | None = None


class RankedListData(BaseModel):
    header_label: str | None = None
    show_bars: bool | None = True
    items: list[RankedListItemData] = Field(default_factory=list)


class DataTableData(BaseModel):
    header_label: str | None = None
    variant: str | None = None  # "standard" | "comparison"
    columns: list[str] = Field(default_factory=list)
    rows: list[list[str | float | int]] = Field(default_factory=list)
    highlight_row: int | None = None
    highlight_col: int | None = None
    highlight_key: str | None = None
    show_data_bars: bool | None = False
    annotation: str | None = None


class BeforeAfterStateData(BaseModel):
    label: str | None = None
    title: str
    value: float | int | str | None = None
    unit: str | None = None
    subtitle: str | None = None
    image: str | None = None
    icon: str | None = None


class BeforeAfterData(BaseModel):
    header_label: str | None = None
    variant: str | None = None  # "numeric" | "visual"
    tone: str | None = None     # "neutral" | "positive" | "negative"
    before: BeforeAfterStateData
    after: BeforeAfterStateData
    delta: str | None = None
    delta_label: str | None = None


class QuoteCalloutData(BaseModel):
    header_label: str | None = None
    quote: str
    author: str | None = None
    role: str | None = None
    avatar: str | None = "💬"


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
        "ProcessFlow": ProcessFlowData,
        "KPIGrid": KPIGridData,
        "ProgressiveList": ProgressiveListData,
        "RankedList": RankedListData,
        "DataTable": DataTableData,
        "BeforeAfter": BeforeAfterData,
        "QuoteCallout": QuoteCalloutData,
        "IconAnimation": IconAnimationData,
        "StockVideo": StockMediaData,
        "StockImage": StockMediaData,
    }

    # Alias mapping for space-separated variants
    ALIASES = {
        "Stock Video": "StockVideo",
        "Stock Image": "StockImage",
        "Icon Animation": "IconAnimation",
        "Process Flow": "ProcessFlow",
        "KPI Grid": "KPIGrid",
        "KpiGrid": "KPIGrid",
        "KPI_Grid": "KPIGrid",
        "Progressive List": "ProgressiveList",
        "Progressive_List": "ProgressiveList",
        "Ranked List": "RankedList",
        "Ranked_List": "RankedList",
        "Data Table": "DataTable",
        "Data_Table": "DataTable",
        "Before After": "BeforeAfter",
        "Before_After": "BeforeAfter",
        "Quote Callout": "QuoteCallout",
        "Quote_Callout": "QuoteCallout",
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
            "ProcessFlow": ComponentDefinition(
                component="ProcessFlow",
                data_model=ProcessFlowData,
                supported_events=["attention_shift"],
            ),
            "KPIGrid": ComponentDefinition(
                component="KPIGrid",
                data_model=KPIGridData,
                supported_events=["attention_shift"],
            ),
            "ProgressiveList": ComponentDefinition(
                component="ProgressiveList",
                data_model=ProgressiveListData,
                supported_events=["attention_shift"],
            ),
            "RankedList": ComponentDefinition(
                component="RankedList",
                data_model=RankedListData,
                supported_events=["attention_shift"],
            ),
            "DataTable": ComponentDefinition(
                component="DataTable",
                data_model=DataTableData,
                supported_events=["attention_shift"],
            ),
            "BeforeAfter": ComponentDefinition(
                component="BeforeAfter",
                data_model=BeforeAfterData,
                supported_events=["attention_shift"],
            ),
            "QuoteCallout": ComponentDefinition(
                component="QuoteCallout",
                data_model=QuoteCalloutData,
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

        if canonical == "Typography":
            text_val = str(data.get("text") or data.get("headline") or data.get("title") or narration_text or visual_goal or "").strip()
            if text_val:
                data["text"] = text_val

            if not data.get("variant") and text_val:
                if text_val.endswith("?"):
                    data["variant"] = "question"
                    data["align"] = data.get("align") or "center"
                elif text_val.startswith('"') or text_val.startswith("'"):
                    data["variant"] = "quote"
                    data["align"] = data.get("align") or "left"
                elif data.get("value") is not None:
                    data["variant"] = "metric"
                    data["align"] = data.get("align") or "center"
                else:
                    data["variant"] = "headline"

        elif canonical == "SplitComparison":
            l_lbl = str(data.get("left_label") or data.get("leftLabel") or data.get("left_role") or data.get("leftRole") or "").strip()
            r_lbl = str(data.get("right_label") or data.get("rightLabel") or data.get("right_role") or data.get("rightRole") or "").strip()
            
            if l_lbl:
                data["left_label"] = l_lbl
                data["left_role"] = l_lbl
            if r_lbl:
                data["right_label"] = r_lbl
                data["right_role"] = r_lbl

            if ("left_value" not in data or data["left_value"] is None) and "leftValue" in data:
                data["left_value"] = data["leftValue"]
            if ("right_value" not in data or data["right_value"] is None) and "rightValue" in data:
                data["right_value"] = data["rightValue"]

            if not data.get("tone") and (l_lbl or r_lbl):
                combined_roles = f"{l_lbl} {r_lbl}".lower()
                if any(w in combined_roles for w in ("bull", "bear", "win", "loss", "profit")):
                    data["tone"] = "positive_negative"
                elif any(w in combined_roles for w in ("before", "after", "prior", "post")):
                    data["tone"] = "before_after"
                else:
                    data["tone"] = "neutral"

            if not data.get("variant"):
                data["variant"] = "versus" if data.get("comparison_label") else "cards"

        elif canonical == "NumberCounter":
            if ("end_value" not in data or data.get("end_value") is None) and "endValue" in data:
                data["end_value"] = data["endValue"]

            if "end_value" not in data or data.get("end_value") is None:
                if "values" in data and isinstance(data["values"], list) and len(data["values"]) > 0:
                    data["end_value"] = float(data["values"][0])
                else:
                    search_text = f"{visual_goal} {data.get('label', '')} {narration_text}"
                    candidates = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", search_text)
                    if candidates:
                        clean_num = float(candidates[-1].replace(",", "")) if len(candidates) > 1 and "%" not in candidates[-1] else float(candidates[0].replace(",", ""))
                        data["end_value"] = clean_num

            u_str = str(data.get("unit") or "").strip()
            if u_str and not data.get("prefix") and not data.get("suffix"):
                if u_str in ("$", "₹", "€"):
                    data["prefix"] = u_str
                elif u_str.startswith("$") or u_str.startswith("₹") or u_str.startswith("€"):
                    data["prefix"] = u_str[0]
                    data["suffix"] = u_str[1:]
                else:
                    data["suffix"] = u_str

            if not data.get("variant"):
                start_val = data.get("start_value", 0)
                data["variant"] = "change" if (start_val and start_val != 0) else "single"

        elif canonical == "Charts":
            ct = str(data.get("chart_type") or data.get("chartType") or "bar").lower()
            if ct in ("horizontal_bar", "horizontalbar", "hbar"):
                data["chart_type"] = "horizontal_bar"
            elif ct in ("pie", "donut"):
                data["chart_type"] = "pie"
            elif ct in ("line", "trend"):
                data["chart_type"] = "line"
            elif ct in ("bar",):
                data["chart_type"] = "bar"

            h_lbl = data.get("highlight_label") or data.get("highlightLabel")
            labels = data.get("labels") or []
            if h_lbl and isinstance(labels, list) and data.get("highlight_index") is None:
                for idx, lbl in enumerate(labels):
                    if str(lbl).lower() == str(h_lbl).lower():
                        data["highlight_index"] = idx
                        break

        elif canonical == "Timeline":
            raw_events = data.get("events")
            raw_steps = data.get("steps") or data.get("labels")
            normalized_events = []

            if isinstance(raw_events, list):
                for idx, ev in enumerate(raw_events):
                    if isinstance(ev, str):
                        normalized_events.append({"date": f"Phase {idx+1}", "title": ev, "type": "normal"})
                    elif isinstance(ev, dict) and ("title" in ev or "event" in ev or "label" in ev):
                        d_val = str(ev.get("date") or ev.get("year") or ev.get("period") or f"Phase {idx+1}")
                        t_val = str(ev.get("title") or ev.get("event") or ev.get("label"))
                        normalized_events.append({
                            "date": d_val,
                            "title": t_val,
                            "subtitle": ev.get("subtitle") or ev.get("description"),
                            "value": ev.get("value"),
                            "type": ev.get("type") or "normal",
                            "icon": ev.get("icon"),
                        })

            if not normalized_events and isinstance(raw_steps, list):
                for idx, step in enumerate(raw_steps):
                    if isinstance(step, str):
                        yr = re.search(r"\b(19\d\d|20\d\d)\b", step)
                        date_str = yr.group(1) if yr else f"Phase {idx+1}"
                        clean_title = step if not yr else step.replace(yr.group(1), "").strip(" -:")
                        clean_title = clean_title or step
                        normalized_events.append({"date": date_str, "title": clean_title, "type": "normal"})
                    elif isinstance(step, dict) and ("title" in step or "label" in step):
                        d_val = str(step.get("date") or step.get("year") or f"Phase {idx+1}")
                        t_val = str(step.get("title") or step.get("label"))
                        normalized_events.append({
                            "date": d_val,
                            "title": t_val,
                            "subtitle": step.get("subtitle"),
                            "value": step.get("value"),
                            "type": step.get("type") or "normal",
                            "icon": step.get("icon"),
                        })

            data["events"] = normalized_events
            if normalized_events:
                data["steps"] = [f"{e['date']}: {e['title']}" for e in normalized_events]

        elif canonical == "ProcessFlow":
            raw_steps = data.get("steps")
            normalized_steps = []
            if isinstance(raw_steps, list):
                total_count = len(raw_steps)
                for idx, item in enumerate(raw_steps):
                    if isinstance(item, str):
                        step_type = "cause" if idx == 0 else ("outcome" if idx == total_count - 1 else "step")
                        normalized_steps.append({
                            "title": item,
                            "type": step_type,
                        })
                    elif isinstance(item, dict) and ("title" in item or "name" in item or "label" in item):
                        t_val = item.get("title") or item.get("name") or item.get("label")
                        step_type = item.get("type") or ("cause" if idx == 0 else ("outcome" if idx == total_count - 1 else "step"))
                        normalized_steps.append({
                            "title": str(t_val),
                            "subtitle": item.get("subtitle"),
                            "type": step_type,
                            "value": item.get("value"),
                            "connector_label": item.get("connector_label") or item.get("connectorLabel") or item.get("relationship"),
                            "icon": item.get("icon"),
                        })
            data["steps"] = normalized_steps

        elif canonical == "KPIGrid":
            raw_kpis = data.get("kpis")
            feat_idx = data.get("featured_index", 0)
            normalized_kpis = []
            if isinstance(raw_kpis, list):
                for idx, item in enumerate(raw_kpis):
                    if isinstance(item, dict) and ("label" in item or "title" in item or "name" in item):
                        lbl = item.get("label") or item.get("title") or item.get("name")
                        val = item.get("value") if "value" in item and item["value"] is not None else 0
                        is_prim = item.get("is_primary") if "is_primary" in item else (idx == feat_idx)
                        normalized_kpis.append({
                            "label": str(lbl),
                            "value": val,
                            "unit": item.get("unit"),
                            "trend": item.get("trend"),
                            "subtitle": item.get("subtitle") or item.get("period"),
                            "icon": item.get("icon"),
                            "is_primary": bool(is_prim),
                        })
            if not normalized_kpis and "labels" in data and "values" in data and isinstance(data["labels"], list) and isinstance(data["values"], list):
                for idx, (lbl, val) in enumerate(zip(data["labels"], data["values"])):
                    normalized_kpis.append({"label": str(lbl), "value": val, "unit": data.get("unit"), "is_primary": (idx == 0)})

            if normalized_kpis and not any(k.get("is_primary") for k in normalized_kpis):
                if 0 <= feat_idx < len(normalized_kpis):
                    normalized_kpis[feat_idx]["is_primary"] = True
                else:
                    normalized_kpis[0]["is_primary"] = True

            data["kpis"] = normalized_kpis

        elif canonical == "ProgressiveList":
            raw_items = data.get("items")
            normalized_items = []
            if isinstance(raw_items, list):
                for item in raw_items:
                    if isinstance(item, str):
                        normalized_items.append({"title": item, "text": item})
                    elif isinstance(item, dict) and ("title" in item or "text" in item or "label" in item):
                        t_val = item.get("title") or item.get("text") or item.get("label")
                        normalized_items.append({
                            "title": str(t_val),
                            "text": str(t_val),
                            "subtitle": item.get("subtitle") or item.get("description"),
                            "icon": item.get("icon"),
                            "highlight": bool(item.get("highlight", False)),
                            "value": item.get("value"),
                        })
            if not normalized_items:
                alt_key = next((k for k in ("bullets", "list_items", "steps", "rules") if k in data and isinstance(data[k], list)), None)
                if alt_key:
                    for item in data[alt_key]:
                        if isinstance(item, str):
                            normalized_items.append({"title": item, "text": item})
                        elif isinstance(item, dict) and ("title" in item or "text" in item or "label" in item):
                            t_val = item.get("title") or item.get("text") or item.get("label")
                            normalized_items.append({
                                "title": str(t_val),
                                "text": str(t_val),
                                "subtitle": item.get("subtitle") or item.get("description"),
                                "icon": item.get("icon"),
                                "highlight": bool(item.get("highlight", False)),
                                "value": item.get("value"),
                            })

            if not data.get("variant") and normalized_items:
                has_subtitles = any(k.get("subtitle") for k in normalized_items)
                data["variant"] = "detailed" if has_subtitles else "compact"

            data["items"] = normalized_items

        elif canonical == "RankedList":
            raw_items = data.get("items")
            normalized_items = []

            def extract_num(val_str: Any) -> float | None:
                if isinstance(val_str, (int, float)):
                    return float(val_str)
                if not val_str:
                    return None
                matches = re.findall(r"[\d,]+(?:\.\d+)?", str(val_str))
                if matches:
                    try:
                        return float(matches[0].replace(",", ""))
                    except ValueError:
                        return None
                return None

            if isinstance(raw_items, list):
                for idx, item in enumerate(raw_items):
                    if isinstance(item, str):
                        normalized_items.append({"rank": idx + 1, "title": item})
                    elif isinstance(item, dict) and ("title" in item or "name" in item or "text" in item):
                        title = item.get("title") or item.get("name") or item.get("text")
                        rank = item.get("rank") if item.get("rank") is not None else (idx + 1)
                        val = item.get("value")
                        num_val = item.get("numeric_value") or item.get("numericValue") or extract_num(val)
                        normalized_items.append({
                            "rank": rank,
                            "title": str(title),
                            "subtitle": item.get("subtitle"),
                            "value": val,
                            "numeric_value": num_val,
                            "badge": item.get("badge"),
                            "change": item.get("change") or item.get("rank_change"),
                            "logo": item.get("logo"),
                            "icon": item.get("icon"),
                        })
            data["items"] = normalized_items

        elif canonical == "DataTable":
            raw_cols = data.get("columns")
            raw_rows = data.get("rows")
            normalized_cols = [str(c) for c in raw_cols] if isinstance(raw_cols, list) else []
            normalized_rows = []
            if isinstance(raw_rows, list):
                for row in raw_rows:
                    if isinstance(row, list):
                        normalized_rows.append(row)
                    elif isinstance(row, dict):
                        if not normalized_cols:
                            normalized_cols = list(row.keys())
                        normalized_rows.append([row.get(col, "") for col in normalized_cols])

            data["columns"] = normalized_cols
            data["rows"] = normalized_rows

            hk = data.get("highlight_key") or data.get("highlightKey")
            if hk and data.get("highlight_row") is None and normalized_rows:
                for idx, r in enumerate(normalized_rows):
                    if r and str(r[0]).lower() == str(hk).lower():
                        data["highlight_row"] = idx
                        break

        elif canonical == "BeforeAfter":
            before_val = data.get("before")
            after_val = data.get("after")

            if isinstance(before_val, str):
                before_val = {"label": "BEFORE", "title": before_val}
            elif isinstance(before_val, dict):
                before_val.setdefault("label", "BEFORE")
                if "title" not in before_val:
                    if data.get("before_title") or data.get("left_role"):
                        before_val["title"] = data.get("before_title") or data.get("left_role")
            elif data.get("before_title") or data.get("left_role") or data.get("left_value"):
                before_val = {
                    "label": "BEFORE",
                    "title": data.get("before_title") or data.get("left_role") or "",
                    "value": data.get("left_value"),
                    "unit": data.get("left_unit"),
                    "subtitle": data.get("left_label"),
                }

            if isinstance(after_val, str):
                after_val = {"label": "AFTER", "title": after_val}
            elif isinstance(after_val, dict):
                after_val.setdefault("label", "AFTER")
                if "title" not in after_val:
                    if data.get("after_title") or data.get("right_role"):
                        after_val["title"] = data.get("after_title") or data.get("right_role")
            elif data.get("after_title") or data.get("right_role") or data.get("right_value"):
                after_val = {
                    "label": "AFTER",
                    "title": data.get("after_title") or data.get("right_role") or "",
                    "value": data.get("right_value"),
                    "unit": data.get("right_unit"),
                    "subtitle": data.get("right_label"),
                }

            if before_val:
                data["before"] = before_val
            if after_val:
                data["after"] = after_val

            if not data.get("variant") and (before_val or after_val):
                bv = before_val.get("value") if isinstance(before_val, dict) else None
                av = after_val.get("value") if isinstance(after_val, dict) else None
                data["variant"] = "numeric" if (bv or av) else "visual"

            if not data.get("tone"):
                data["tone"] = "neutral"

        elif canonical == "QuoteCallout":
            quote_text = data.get("quote") or data.get("text") or data.get("label") or visual_goal
            if quote_text:
                data["quote"] = str(quote_text)
            if data.get("speaker") or data.get("source"):
                data["author"] = data.get("speaker") or data.get("source")

        elif canonical == "IconAnimation":
            if data.get("header_label") or visual_goal:
                data.setdefault("label", data.get("header_label") or visual_goal)

        elif canonical == "Typography":
            if not data.get("text") and (data.get("header_label") or visual_goal):
                data["text"] = data.get("header_label") or visual_goal

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
