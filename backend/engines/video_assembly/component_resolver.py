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

        # ─────────────────────────────────────────────────────────────
        # Route each component: map snake_case Python data keys
        # to camelCase TypeScript props matching types.ts interfaces.
        # ─────────────────────────────────────────────────────────────

        if canonical == "SplitComparison":
            # types.ts → SplitComparisonProps
            props = {
                "headerLabel": data.get("header_label"),
                "comparisonLabel": data.get("comparison_label"),
                "variant": data.get("variant"),
                "tone": data.get("tone"),
                "leftRole": data.get("left_role"),
                "leftLabel": data.get("left_label"),
                "leftValue": data.get("left_value"),
                "leftUnit": data.get("left_unit"),
                "rightRole": data.get("right_role"),
                "rightLabel": data.get("right_label"),
                "rightValue": data.get("right_value"),
                "rightUnit": data.get("right_unit"),
                "delta": data.get("delta"),
                "winner": data.get("winner"),
            }

        elif canonical == "Typography":
            # types.ts → TypographyProps
            props = {
                "headerLabel": data.get("header_label"),
                "text": data.get("text"),
                "subtitle": data.get("subtitle"),
                "variant": data.get("variant"),
                "highlight": data.get("highlight"),
                "align": data.get("align"),
                "value": data.get("value"),
                "author": data.get("author"),
            }

        elif canonical == "NumberCounter":
            # types.ts → NumberCounterProps
            props = {
                "headerLabel": data.get("header_label"),
                "variant": data.get("variant"),
                "startValue": data.get("start_value"),
                "endValue": data.get("end_value"),
                "label": data.get("label"),
                "prefix": data.get("prefix"),
                "suffix": data.get("suffix"),
                "unit": data.get("unit"),
                "precision": data.get("precision"),
                "delta": data.get("delta"),
                "subtitle": data.get("subtitle"),
            }

        elif canonical == "Charts":
            # types.ts → ChartsProps
            props = {
                "headerLabel": data.get("header_label"),
                "chartType": data.get("chart_type"),
                "labels": data.get("labels"),
                "values": data.get("values"),
                "unit": data.get("unit"),
                "highlightIndex": data.get("highlight_index"),
                "highlightLabel": data.get("highlight_label"),
                "annotation": data.get("annotation"),
                "centerLabel": data.get("center_label"),
                "centerValue": data.get("center_value"),
            }

        elif canonical == "Timeline":
            # types.ts → TimelineProps (events: TimelineEvent[])
            # TimelineEvent fields: date, title, subtitle, value, type, icon
            # No snake→camel conversion needed for event objects
            props = {
                "headerLabel": data.get("header_label"),
                "variant": data.get("variant"),
                "events": data.get("events"),
                "steps": data.get("steps"),
            }

        elif canonical == "ProcessFlow":
            # types.ts → ProcessFlowProps (steps: ProcessStep[])
            # ProcessStep: title, subtitle, type, value, connectorLabel, icon
            # Need: connector_label → connectorLabel
            raw_steps = data.get("steps") or []
            mapped_steps = []
            for step in raw_steps:
                if isinstance(step, dict):
                    mapped_steps.append({
                        "title": step.get("title"),
                        "subtitle": step.get("subtitle"),
                        "type": step.get("type"),
                        "value": step.get("value"),
                        "connectorLabel": step.get("connector_label"),
                        "icon": step.get("icon"),
                    })
            props = {
                "headerLabel": data.get("header_label"),
                "layout": data.get("layout"),
                "steps": mapped_steps,
            }

        elif canonical == "KPIGrid":
            # types.ts → KPIGridProps (kpis: KPICard[])
            # KPICard: label, value, unit, trend, subtitle, icon, is_primary
            # No snake→camel conversion needed for kpi objects
            props = {
                "headerLabel": data.get("header_label"),
                "featuredIndex": data.get("featured_index"),
                "kpis": data.get("kpis"),
            }

        elif canonical == "ProgressiveList":
            # types.ts → ProgressiveListProps (items: ProgressiveListItem[])
            # ProgressiveListItem: title, text, subtitle, icon, highlight, value
            # No snake→camel conversion needed for item objects
            props = {
                "headerLabel": data.get("header_label"),
                "variant": data.get("variant"),
                "items": data.get("items"),
            }

        elif canonical == "RankedList":
            # types.ts → RankedListProps (items: RankedListItem[])
            # RankedListItem: title, rank, subtitle, value, numericValue, badge, change, logo, icon
            # Need: numeric_value → numericValue
            raw_items = data.get("items") or []
            mapped_items = []
            for item in raw_items:
                if isinstance(item, dict):
                    mapped_items.append({
                        "title": item.get("title"),
                        "rank": item.get("rank"),
                        "subtitle": item.get("subtitle"),
                        "value": item.get("value"),
                        "numericValue": item.get("numeric_value"),
                        "badge": item.get("badge"),
                        "change": item.get("change"),
                        "logo": item.get("logo"),
                        "icon": item.get("icon"),
                    })
            props = {
                "headerLabel": data.get("header_label"),
                "showBars": data.get("show_bars"),
                "items": mapped_items,
            }

        elif canonical == "DataTable":
            # types.ts → DataTableProps
            props = {
                "headerLabel": data.get("header_label"),
                "variant": data.get("variant"),
                "columns": data.get("columns"),
                "rows": data.get("rows"),
                "highlightRow": data.get("highlight_row"),
                "highlightCol": data.get("highlight_col"),
                "highlightKey": data.get("highlight_key"),
                "showDataBars": data.get("show_data_bars"),
                "annotation": data.get("annotation"),
            }

        elif canonical == "BeforeAfter":
            # types.ts → BeforeAfterProps (before/after: BeforeAfterState)
            # BeforeAfterState: label, title, value, unit, subtitle, image, icon
            # No snake→camel conversion needed for before/after objects
            props = {
                "headerLabel": data.get("header_label"),
                "variant": data.get("variant"),
                "tone": data.get("tone"),
                "before": data.get("before"),
                "after": data.get("after"),
                "delta": data.get("delta"),
                "deltaLabel": data.get("delta_label"),
            }

        elif canonical == "QuoteCallout":
            # types.ts → QuoteCalloutProps
            props = {
                "headerLabel": data.get("header_label"),
                "quote": data.get("quote"),
                "author": data.get("author"),
                "role": data.get("role"),
                "avatar": data.get("avatar"),
            }

        elif canonical == "IconAnimation":
            # types.ts → MediaComponentProps
            props = {
                "headerLabel": data.get("header_label"),
                "icon": data.get("icon"),
                "text": data.get("label"),
            }

        elif canonical in ("StockVideo", "StockImage"):
            # types.ts → MediaComponentProps (minimal — asset handled separately)
            props = {
                "headerLabel": data.get("header_label"),
            }

        else:
            raise ValueError(f"Unsupported component_id: '{canonical}'.")

        return ComponentSpec(
            component_id=canonical,
            props=props,
        )
