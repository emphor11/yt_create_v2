from __future__ import annotations

import json
import re
from typing import Any
from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.research_packet import ResearchPacket
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.voice_track import VoiceTrack
from domain.continuous_story_plan import (
    ContinuousStoryDraft,
    ContinuousStoryPlanArtifact,
    VALID_ZONES,
)
from domain.validators.continuous_story_plan_validator import ContinuousStoryPlanValidator
from engines.continuous_story_draft_validator import validate_story_draft
from engines.continuous_story_compiler import ContinuousStoryCompiler, resolve_anchor_frame
from providers.llm_provider import LLMJsonRequest, LLMMessage, LLMProvider


_MONEY_RE = re.compile(
    r"(?<![A-Za-z])(?:₹|rs(?:\.)?|inr)\s*(\d[\d,]*(?:\.\d+)?)\s*(lakh|lakhs|crore|crores)?",
    re.IGNORECASE,
)
_PERCENT_RE = re.compile(r"([\d]+(?:\.\d+)?)\s*%")
_BPS_RE = re.compile(r"([\d]+(?:\.\d+)?)\s*basis\s*points?", re.IGNORECASE)


def _numeric_facts_from_research(research_packet: ResearchPacket) -> dict[str, Any]:
    """Promote explicit numeric evidence into typed compiler facts."""
    facts: dict[str, Any] = {}
    counter = 1
    for source in [
        *research_packet.verified_facts,
        *research_packet.statistics,
        *research_packet.examples,
    ]:
        for match in _MONEY_RE.finditer(source):
            value = float(match.group(1).replace(",", ""))
            unit = (match.group(2) or "").lower()
            if unit.startswith("lakh"):
                value *= 100_000
            elif unit.startswith("crore"):
                value *= 10_000_000
            value = int(value) if value.is_integer() else value
            facts[f"research_money_{counter}"] = {
                "value": value,
                "format": "currency_inr",
                "label": "Research monetary fact",
                "subtitle": source[:120],
                "provenance": {"formula": "research_grounded", "source": source},
            }
            counter += 1
        for match in _PERCENT_RE.finditer(source):
            value = float(match.group(1))
            value = int(value) if value.is_integer() else value
            facts[f"research_percent_{counter}"] = {
                "value": value,
                "format": "percentage",
                "label": "Research percentage fact",
                "subtitle": source[:120],
                "provenance": {"formula": "research_grounded", "source": source},
            }
            counter += 1
        for match in _BPS_RE.finditer(source):
            value = float(match.group(1))
            value = int(value) if value.is_integer() else value
            facts[f"research_bps_{counter}"] = {
                "value": value,
                "format": "basis_points",
                "label": "Research basis-point fact",
                "subtitle": source[:120],
                "provenance": {"formula": "research_grounded", "source": source},
            }
            counter += 1

    if not facts:
        num_re = re.compile(r"\b(\d[\d,]*(?:\.\d+)?)\b")
        for source in [*research_packet.verified_facts, *research_packet.statistics, *research_packet.examples]:
            for match in num_re.finditer(source):
                val_str = match.group(1).replace(",", "")
                try:
                    val = float(val_str)
                    if val <= 0:
                        continue
                    val = int(val) if val.is_integer() else val
                    facts[f"research_num_{counter}"] = {
                        "value": val,
                        "format": "plain",
                        "label": "Research numeric fact",
                        "subtitle": source[:120],
                        "provenance": {"formula": "research_grounded", "source": source},
                    }
                    counter += 1
                except ValueError:
                    continue

    return facts


def _normalize_zone(val: Any, default: str = "center") -> str:
    """Safely normalizes arbitrary layout inputs into one of the 12 strict ZoneNames."""
    if isinstance(val, str) and val in VALID_ZONES:
        return val
    if isinstance(val, str):
        aliases = {
            "left": "center_left",
            "right": "center_right",
            "top": "top_center",
            "bottom": "bottom_center",
        }
        if val in aliases:
            return aliases[val]
    if isinstance(val, dict):
        if "right_of" in val:
            return "center_right"
        if "left_of" in val:
            return "center_left"
        if "below" in val:
            return "bottom_center"
        if "above" in val:
            return "top_center"
    return default


def _safe_contract_repair(payload: dict[str, Any]) -> dict[str, Any]:
    """Apply only lossless safety repairs after an LLM repair fails.

    Enforces the atomic schema:
    1. Removes parent_id and ensures top-level independence.
    2. Normalizes layout to valid 12-zone names.
    3. Retains valid grounded objects.
    """
    repaired = dict(payload)
    objects: list[dict[str, Any]] = []
    for raw in repaired.get("objects", []):
        if not isinstance(raw, dict):
            continue
        obj = dict(raw)
        obj.pop("parent_id", None)
        obj.pop("content", None)
        obj["layout"] = _normalize_zone(obj.get("layout"), default="center")

        obj_type = obj.get("type")
        if obj_type != "connector":
            obj.pop("from_id", None)
            obj.pop("to_id", None)
            obj.pop("label", None)
        else:
            obj["layout"] = "center"

        if obj_type != "chart":
            obj.pop("chart_type", None)
        if obj_type != "image":
            obj.pop("asset_id", None)

        if obj_type in {"number", "chart"} and not (obj.get("fact_id") or obj.get("value_fact_id")):
            continue
        objects.append(obj)

    valid_ids = {obj.get("id") for obj in objects}
    repaired["objects"] = objects

    events: list[dict[str, Any]] = []
    for raw in repaired.get("events", repaired.get("timeline", [])):
        if not isinstance(raw, dict):
            continue
        event = dict(raw)
        if "anchor" not in event and event.get("speech_anchor"):
            event["anchor"] = event.pop("speech_anchor")
        if isinstance(event.get("anchor"), list):
            event["anchor"] = " ".join(str(p) for p in event["anchor"])
        if event.get("action") == "create_connector":
            event["action"] = "connect"
        if event.get("action") == "move":
            event["to"] = _normalize_zone(event.get("to"), default="center_right")
        if event.get("target_id") not in valid_ids:
            continue
        events.append(event)

    repaired["events"] = events
    repaired.pop("timeline", None)
    return repaired


def _safe_temporal_repair(
    draft: ContinuousStoryDraft,
    word_timestamps: list[dict[str, Any]],
) -> ContinuousStoryDraft:
    """Re-anchor lifecycle actions to existing spoken entry anchors.

    Ensures that actions only occur after their target elements enter.
    """
    objects_by_id = {obj.id: obj for obj in draft.objects}
    enters: dict[str, tuple[int, str]] = {}
    for event in draft.events:
        anchor = event.anchor if isinstance(event.anchor, str) else " ".join(str(part) for part in event.anchor)
        event.anchor = anchor
        if event.action != "enter":
            continue
        try:
            frame = resolve_anchor_frame(word_timestamps=word_timestamps, anchor_phrase=anchor, fps=30)
            previous = enters.get(event.target_id)
            if previous is None or frame < previous[0]:
                enters[event.target_id] = (frame, event.anchor)
        except Exception:
            continue

    for event in draft.events:
        anchor = event.anchor if isinstance(event.anchor, str) else " ".join(str(part) for part in event.anchor)
        event.anchor = anchor
        if event.action == "enter":
            continue
        required_ids = [event.target_id]
        target = objects_by_id.get(event.target_id)
        if event.action == "connect" and target is not None:
            required_ids = [target.from_id or "", target.to_id or ""]
        required_entries = [enters[item_id] for item_id in required_ids if item_id in enters]
        if len(required_entries) != len(required_ids):
            continue
        required_frame, required_anchor = max(required_entries, key=lambda item: item[0])
        try:
            current_frame = resolve_anchor_frame(word_timestamps=word_timestamps, anchor_phrase=anchor, fps=30)
            if current_frame < required_frame:
                event.anchor = required_anchor
        except Exception:
            event.anchor = required_anchor
    return draft


def build_continuous_story_prompt(
    story_id: str,
    narration_text: str,
    approved_facts: dict[str, Any],
) -> tuple[str, str]:
    """Builds system and user prompts for Gemini visual choreography."""
    system_prompt = (
        "You are an expert visual director and choreography planner for high-retention explanatory video stories.\n"
        "Your task is to produce an atomic, collision-free visual choreography plan (ContinuousStoryDraft) in JSON.\n\n"
        "CORE ARCHITECTURAL RULES: ATOMIC ELEMENTS + 12-ZONE CANVAS\n\n"
        "1. ATOMIC VISUAL ELEMENTS (NO PARENT-CHILD MODEL):\n"
        "   - Do NOT use parent_id. There are no child objects. Every visual element is independent and top-level.\n"
        "   - Supported primitive types: 'card', 'number', 'text', 'chart', 'image', 'connector'.\n"
        "   - 'card': Complete self-contained visual card. Holds its own title, numeric value, subtitle, badge, and visual state.\n"
        "     Allowed fields: id, type ('card'), layout, title, value_fact_id (or fact_id), subtitle, badge, visual_state, accent, purpose.\n"
        "   - 'number': Standalone numeric callout (only when NOT inside a card). Requires fact_id.\n"
        "   - 'text': Standalone headline or title. Requires text.\n"
        "   - 'chart': Factual chart. Requires fact_id and chart_type ('trajectory_area', 'split_bar', 'multi_bar', 'stack').\n"
        "   - 'image': Standalone image visual. Requires asset_id.\n"
        "   - 'connector': Visual arrow between two cards. Requires from_id, to_id, and label.\n\n"
        "2. FIXED 12-ZONE CANVAS LAYOUT SYSTEM (CHESSBOARD SPATIAL RULES):\n"
        "   - The canvas is divided into 9 discrete grid zones plus 3 macro zones.\n"
        "   - You MUST pick exactly ONE layout zone name for every surface element:\n"
        "       top_left       top_center       top_right\n"
        "       center_left    center           center_right\n"
        "       bottom_left    bottom_center    bottom_right\n"
        "       full_screen    full_top         full_bottom\n"
        "   - 'full_screen': Exclusive full-canvas visual (e.g. hero image).\n"
        "   - 'full_bottom': Wide lower area for trajectory charts.\n"
        "   - NEVER output pixel numbers (x, y, width, height) or relative graphs ('right_of', 'below', 'gap').\n\n"
        "3. SPATIAL CONSERVATION & OCCUPANCY SAFETY (NO STACKING):\n"
        "   - Two visible surfaces CANNOT occupy the same zone at the same time.\n"
        "   - An element reserves its zone until it exits. A new element cannot enter an occupied zone.\n"
        "   - To choreograph dynamic relationships:\n"
        "     * E.g. Hero Card 1 enters at 'center'.\n"
        "     * When Card 2 needs to appear, Card 1 MOVES to 'center_left', freeing the center/right area.\n"
        "     * Card 2 enters at 'center_right'.\n"
        "     * A connector links Card 1 and Card 2.\n"
        "     * When introducing a subsequent consequence, exit Card 1 or move it, or place the new visual in an empty zone.\n\n"
        "4. FACT GROUNDING (IMMUTABLE NUMERICAL TRUTH):\n"
        "   - NEVER invent numbers. Every card value, standalone number, or chart MUST reference an approved fact ID via 'value_fact_id' or 'fact_id'.\n"
        "   - For 'transform_number' actions: Specify 'to_fact_id' referencing an approved fact ID.\n\n"
        "5. STORY EVENTS & TEMPORAL ACTIONS:\n"
        "   - Every event MUST have an 'anchor' consisting of 2 to 4 consecutive spoken words from the Narration Text.\n"
        "   - Supported actions:\n"
        "     * 'enter': target enters its assigned zone.\n"
        "     * 'move': target moves to a free destination zone ('to': ZoneName).\n"
        "     * 'transform_number': target card or number updates its value to 'to_fact_id'.\n"
        "     * 'transform_text': target card subtitle or text updates to 'to_text'.\n"
        "     * 'change_visual_state': target changes visual state ('warning', 'danger', 'success', 'dimmed', 'eroded') with optional 'badge'.\n"
        "     * 'connect': connector attaches between two currently visible cards.\n"
        "     * 'exit': target exits canvas with 'direction' ('left', 'right', 'up', 'down', 'fade'), clearing its zone.\n"
        "   - Causality: An object must enter before it can move, transform, connect, or exit. Connectors require both endpoints to be entered.\n\n"
        "ROOT JSON STRUCTURE:\n"
        "   {\n"
        "     \"story_id\": \"...\",\n"
        "     \"objects\": [ ... ],\n"
        "     \"events\": [ ... ]\n"
        "   }\n"
        "Keep the plan focused and cinematic: 3 to 6 atomic surfaces, 1 to 2 connectors, 8 to 14 events. No parent_id. No pixel coordinates."
    )

    facts_summary = []
    for fid, fval in approved_facts.items():
        if isinstance(fval, dict):
            val_display = fval.get("value", "chart_data")
            fmt_display = fval.get("format", "chart")
            label_display = fval.get("label", fid)
            facts_summary.append(f"  - '{fid}': {label_display} (Value: {val_display}, Format: {fmt_display})")
        else:
            facts_summary.append(f"  - '{fid}': {fval}")
    facts_str = "\n".join(facts_summary) if facts_summary else "  (None provided)"
    fact_ids_str = ", ".join(repr(fid) for fid in approved_facts) or "(none)"

    user_prompt = (
        f"STORY ID: {story_id}\n\n"
        f"NARRATION TEXT (Spoken Audio Track):\n"
        f"\"{narration_text}\"\n\n"
        f"APPROVED FACTS (Every card value, number, and chart must reference a 'fact_id' or 'value_fact_id' from this list):\n"
        f"{facts_str}\n\n"
        f"APPROVED FACT IDS: {fact_ids_str}\n"
        "RULES REMINDER:\n"
        "- No parent-child model. Do not write parent_id. Cards hold their own title, value_fact_id, subtitle, and badge.\n"
        "- Use only the 12 spatial layout zone names: top_left, top_center, top_right, center_left, center, center_right, bottom_left, bottom_center, bottom_right, full_screen, full_top, full_bottom.\n"
        "- Prevent stacking: Do not enter a surface into an occupied zone.\n"
        "Output strictly valid ContinuousStoryDraft JSON following all rules."
    )
    return system_prompt, user_prompt


class ContinuousStoryHandler:
    """
    Stage handler for the 'continuous_story' pipeline stage.

    Coordinates:
    1. Parent artifact retrieval (voice_track, script_visual_strategy, research_packet).
    2. Fact extraction and prompt construction.
    3. LLM visual choreography generation (Gemini).
    4. AI draft validation (validate_story_draft).
    5. Deterministic StoryPlan compilation (ContinuousStoryCompiler).
    6. Artifact envelope validation (ContinuousStoryPlanValidator).
    7. Saving the ContinuousStoryPlanArtifact with full parent lineage.
    """

    def __init__(
        self,
        *,
        store: ArtifactStore,
        llm_provider: LLMProvider | None = None,
        artifact_validator: ContinuousStoryPlanValidator | None = None,
        stage_logger: StageLogger | None = None,
        compiler: ContinuousStoryCompiler | None = None,
    ) -> None:
        self.store = store
        self.llm_provider = llm_provider
        self.artifact_validator = artifact_validator or ContinuousStoryPlanValidator()
        self.stage_logger = stage_logger or StageLogger()
        self.compiler = compiler or ContinuousStoryCompiler()

    def run(
        self,
        project_id: str,
        run_id: str,
        mock_draft: ContinuousStoryDraft | dict[str, Any] | None = None,
    ) -> ArtifactRecord:
        existing = self.store.find_artifact_by_type(project_id, run_id, "continuous_story_plan")
        if existing is not None and existing.status not in ("failed", "error"):
            return existing

        start = self.stage_logger.log_start(project_id, run_id, "continuous_story")
        try:
            # 1. Retrieve required parent artifacts
            voice_track_artifact = self.store.require_artifact(
                project_id, run_id, "voice_track", for_stage="continuous_story"
            )
            voice_track = VoiceTrack.model_validate(voice_track_artifact.payload_json)

            strategy_artifact = self.store.require_artifact(
                project_id, run_id, "script_visual_strategy", for_stage="continuous_story"
            )
            strategy = ScriptVisualStrategy.model_validate(strategy_artifact.payload_json)

            research_artifact = self.store.require_artifact(
                project_id, run_id, "research_packet", for_stage="continuous_story"
            )
            research_packet = ResearchPacket.model_validate(research_artifact.payload_json)

            # 2. Resolve approved facts from strategy or research payload
            approved_facts: dict[str, Any] = {}
            if isinstance(strategy_artifact.payload_json, dict) and "approved_facts" in strategy_artifact.payload_json:
                approved_facts = strategy_artifact.payload_json["approved_facts"]
            elif isinstance(research_artifact.payload_json, dict) and "approved_facts" in research_artifact.payload_json:
                approved_facts = research_artifact.payload_json["approved_facts"]
            else:
                approved_facts = _numeric_facts_from_research(research_packet)

            story_id = f"story_{project_id}"
            word_timestamps_raw = [
                ts if isinstance(ts, dict) else ts.model_dump()
                for ts in voice_track.word_timestamps
            ]
            total_duration_ms = int(voice_track.duration_seconds * 1000)

            # 3. Generate visual choreography (Gemini or mock for testing)
            raw_gemini_payload: dict[str, Any] = {}
            if mock_draft is not None:
                if isinstance(mock_draft, dict):
                    draft = ContinuousStoryDraft.model_validate(mock_draft)
                    raw_gemini_payload = mock_draft
                else:
                    draft = mock_draft
                    raw_gemini_payload = mock_draft.model_dump()
            else:
                if self.llm_provider is None:
                    raise RuntimeError("LLMProvider is required for ContinuousStoryHandler when mock_draft is not provided.")

                system_prompt, user_prompt = build_continuous_story_prompt(
                    story_id=story_id,
                    narration_text=voice_track.full_script_text,
                    approved_facts=approved_facts,
                )
                req = LLMJsonRequest(
                    messages=[
                        LLMMessage(role="system", content=system_prompt),
                        LLMMessage(role="user", content=user_prompt),
                    ],
                    schema_name="ContinuousStoryDraft",
                    response_schema=None,
                    temperature=0.0,
                    max_tokens=4096,
                )
                response = self.llm_provider.generate_json(req)
                raw_gemini_payload = response.payload
                try:
                    draft = ContinuousStoryDraft.model_validate(raw_gemini_payload)
                except Exception as first_error:
                    repair_req = LLMJsonRequest(
                        messages=[
                            LLMMessage(
                                role="system",
                                content=(
                                    system_prompt
                                    + "\nReturn only the corrected JSON object. Do not explain the repair."
                                ),
                            ),
                            LLMMessage(
                                role="user",
                                content=(
                                    "Your previous JSON failed the strict atomic 12-zone contract.\n"
                                    f"Validation error: {first_error}\n"
                                    f"Previous JSON: {json.dumps(raw_gemini_payload, ensure_ascii=False)}\n"
                                    f"Approved fact IDs: {', '.join(approved_facts.keys()) or '(none)'}\n"
                                    "Ensure NO parent_id is used. Cards hold their own title, value_fact_id, subtitle, and badge. "
                                    "All layouts must be valid 12-zone names. Return JSON only."
                                ),
                            ),
                        ],
                        schema_name="ContinuousStoryDraftRepair",
                        response_schema=None,
                        temperature=0.0,
                        max_tokens=4096,
                    )
                    repaired = self.llm_provider.generate_json(repair_req)
                    raw_gemini_payload = repaired.payload
                    try:
                        draft = ContinuousStoryDraft.model_validate(raw_gemini_payload)
                    except Exception:
                        raw_gemini_payload = _safe_contract_repair(raw_gemini_payload)
                        draft = ContinuousStoryDraft.model_validate(raw_gemini_payload)

            # 4. Run pre-compilation draft validation (occupancy & temporal simulation)
            draft_validation = validate_story_draft(
                draft=draft,
                approved_facts=approved_facts,
                word_timestamps=word_timestamps_raw,
                total_duration_ms=total_duration_ms,
            )
            if not draft_validation.valid and mock_draft is None and self.llm_provider is not None:
                causal_errors = "; ".join(
                    f"[{error.code}] {error.message}" for error in draft_validation.errors
                )
                repair_req = LLMJsonRequest(
                    messages=[
                        LLMMessage(
                            role="system",
                            content=(
                                system_prompt
                                + "\nReturn only the corrected JSON object. Do not explain the repair."
                            ),
                        ),
                        LLMMessage(
                            role="user",
                            content=(
                                "Your draft passed the JSON contract but failed spatial or temporal validation.\n"
                                f"Errors: {causal_errors}\n"
                                f"Previous JSON: {json.dumps(raw_gemini_payload, ensure_ascii=False)}\n"
                                "Resolve zone collisions: Do not place a new surface into an occupied zone before the old surface exits. "
                                "Resolve causality: An object must enter before moving, transforming, connecting, or exiting. Return JSON only."
                            ),
                        ),
                    ],
                    schema_name="ContinuousStoryDraftTemporalRepair",
                    response_schema=ContinuousStoryDraft.model_json_schema(),
                    temperature=0.0,
                    max_tokens=4096,
                )
                repaired = self.llm_provider.generate_json(repair_req)
                raw_gemini_payload = repaired.payload
                try:
                    draft = ContinuousStoryDraft.model_validate(raw_gemini_payload)
                except Exception:
                    raw_gemini_payload = _safe_contract_repair(raw_gemini_payload)
                    draft = ContinuousStoryDraft.model_validate(raw_gemini_payload)
                draft_validation = validate_story_draft(
                    draft=draft,
                    approved_facts=approved_facts,
                    word_timestamps=word_timestamps_raw,
                    total_duration_ms=total_duration_ms,
                )
                if not draft_validation.valid:
                    draft = _safe_temporal_repair(draft, word_timestamps_raw)
                    draft_validation = validate_story_draft(
                        draft=draft,
                        approved_facts=approved_facts,
                        word_timestamps=word_timestamps_raw,
                        total_duration_ms=total_duration_ms,
                    )
            if not draft_validation.valid:
                error_msgs = [f"[{e.code}] {e.message}" for e in draft_validation.errors]
                raise ValueError(f"Continuous story draft validation failed: {'; '.join(error_msgs)}")

            # 5. Deterministic compilation
            fixture_context = {
                "story_id": draft.story_id,
                "approved_facts": approved_facts,
                "word_timestamps": word_timestamps_raw,
                "total_duration_ms": total_duration_ms,
                "audio_file": voice_track.audio_file_name,
                "narration_text": voice_track.full_script_text,
            }
            compiled_plan = self.compiler.compile(draft, fixture_context)

            # 6. Build and validate artifact envelope
            artifact_model = ContinuousStoryPlanArtifact.from_compiled_plan(
                plan=compiled_plan,
                draft=draft,
                audio_storage_key=voice_track.storage_key,
            )
            validation_result = self.artifact_validator.validate(artifact_model)

            # 7. Persist to ArtifactStore with lineage
            payload_data = artifact_model.model_dump()
            payload_data["raw_gemini_draft"] = raw_gemini_payload

            artifact_record = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="continuous_story_plan",
                schema_version=artifact_model.schema_version,
                payload_json=payload_data,
                parent_artifact_roles_json={
                    "voice_track": voice_track_artifact.id,
                    "script_visual_strategy": strategy_artifact.id,
                    "research_packet": research_artifact.id,
                },
                validation_json=validation_result,
            )
            self.stage_logger.log_finish(project_id, run_id, "continuous_story", start_time=start)
            return artifact_record
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "continuous_story", error=exc, start_time=start)
            raise
