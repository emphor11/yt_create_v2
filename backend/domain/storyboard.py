"""Scene Storyboarder domain contract.

Core Architecture Principles:
- VisualIntent describes WHAT the viewer must understand (semantic context, entities,
  measurements, temporal/causal/comparison context, and relationship_type).
- VisualIntent.relationship_type is strictly SEMANTIC METADATA, NEVER a deterministic
  mapping or lookup to visual primitives, macro zones, or visual templates.
- The Storyboarder receives the complete VisualIntent and creatively decides HOW to
  communicate that understanding visually using the 13 canonical primitives.
- Two intents with the same relationship_type can produce completely different visual
  primitives, layouts, or motion based on their distinct storytelling needs.
- The Compiler deterministically resolves the storyboard into executable primitive,
  layout, and timing data.

Strict Architectural Boundaries:
- NO pixel coordinates (x, y, width, height)
- NO frame numbers (start_frame, duration_frames)
- NO timestamps (seconds, timecodes)
- NO Remotion components or raw renderer props
- NO high-level composition/template names ('card', 'hero', 'comparison', etc.)
- All styling is expressed via semantic design tokens/roles.
"""
from __future__ import annotations

from enum import Enum
import re
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

from domain.primitives.common import CanonicalCapabilityType, FORBIDDEN_COMPOSITION_TYPES
from domain.narrative_plan import NarrativePlan
from domain.visual_intent import VisualIntent
from domain.visual_intent_artifact import VisualIntentArtifact


# -----------------------------------------------------------------------------
# 1. Macro Layout: Semantic Screen Zones
# -----------------------------------------------------------------------------
class MacroScreenZone(str, Enum):
    """Semantic screen zones on the 1080p canvas."""
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    SPLIT_LEFT = "split_left"
    SPLIT_RIGHT = "split_right"
    SPLIT_TOP = "split_top"
    SPLIT_BOTTOM = "split_bottom"
    FULL_SCREEN = "full_screen"


# -----------------------------------------------------------------------------
# 2. Micro Layout: Hierarchical Group Container Flow
# -----------------------------------------------------------------------------
class ContainerFlow(str, Enum):
    """Directional flow of children inside a group container."""
    FREE = "free"
    ROW = "row"
    COLUMN = "column"


class FlowAlignment(str, Enum):
    """Cross-axis alignment of children."""
    START = "start"
    CENTER = "center"
    END = "end"
    STRETCH = "stretch"


class FlowJustification(str, Enum):
    """Main-axis distribution of children."""
    START = "start"
    CENTER = "center"
    END = "end"
    SPACE_BETWEEN = "space_between"
    SPACE_AROUND = "space_around"


class SemanticSpacing(str, Enum):
    """Semantic spacing scale for gap and padding."""
    NONE = "none"
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"


class MicroLayoutFlow(BaseModel):
    """Auto-layout container specifications for group primitives."""
    model_config = ConfigDict(extra="forbid")

    flow: ContainerFlow = ContainerFlow.COLUMN
    alignment: FlowAlignment = FlowAlignment.START
    justification: FlowJustification = FlowJustification.START
    gap: SemanticSpacing = SemanticSpacing.MD
    padding: SemanticSpacing = SemanticSpacing.MD


# -----------------------------------------------------------------------------
# 3. Semantic Design Tokens & Roles
# -----------------------------------------------------------------------------
class SemanticColorRole(str, Enum):
    """Semantic color roles resolved by the design system."""
    SURFACE = "surface"
    SURFACE_ELEVATED = "surface_elevated"
    BORDER = "border"
    PRIMARY_TEXT = "primary_text"
    SECONDARY_TEXT = "secondary_text"
    MUTED = "muted"
    ACCENT = "accent"
    WARNING = "warning"
    SUCCESS = "success"
    DANGER = "danger"
    INFO = "info"


class SemanticTypographyRole(str, Enum):
    """Semantic typography scale roles."""
    DISPLAY = "display"          # Hero metric or massive focal statement
    HEADLINE = "headline"        # Scene main title
    SUBHEADLINE = "subheadline"  # Section subtitle or major card value
    BODY = "body"                # Standard explanatory statement
    CAPTION = "caption"          # Micro-label, card eyebrow, or unit
    EYEBROW = "eyebrow"          # Categorical badge tag, uppercase


class SemanticRadiusRole(str, Enum):
    """Semantic corner radius scale."""
    NONE = "none"
    SM = "sm"
    CARD = "card"
    CHIP = "chip"
    PILL = "pill"


class SemanticElevationRole(str, Enum):
    """Semantic elevation and shadow role."""
    NONE = "none"
    SUBTLE = "subtle"
    CARD = "card"
    GLOW = "glow"


class SemanticStyleIntent(BaseModel):
    """Visual style expressed purely through semantic design tokens."""
    model_config = ConfigDict(extra="forbid")

    fill_role: SemanticColorRole | None = None
    stroke_role: SemanticColorRole | None = None
    text_color_role: SemanticColorRole | None = None
    typography_role: SemanticTypographyRole | None = None
    radius_role: SemanticRadiusRole | None = None
    elevation_role: SemanticElevationRole | None = None
    opacity: float | None = Field(default=1.0, ge=0.0, le=1.0)


# -----------------------------------------------------------------------------
# 4. Prohibited Downstream Keys Check
# -----------------------------------------------------------------------------
PROHIBITED_DOWNSTREAM_KEYS = {
    "x", "y", "left", "top", "right", "bottom", "width", "height", "pixel", "px",
    "frame", "frames", "start_frame", "exit_frame", "duration_frames",
    "timestamp", "timestamps", "seconds", "time_seconds",
    "remotion", "remotion_component", "component_name",
}


def check_for_prohibited_keys(data: dict[str, Any], path: str = "") -> None:
    """Recursively checks that no downstream geometry or frame numbers exist."""
    for key, value in data.items():
        current_path = f"{path}.{key}" if path else key
        if key.lower() in PROHIBITED_DOWNSTREAM_KEYS:
            raise ValueError(
                f"Prohibited downstream property '{current_path}' found in Storyboarder output. "
                "The Storyboarder must never output pixel coordinates, frame numbers, or timestamps."
            )
        if isinstance(value, dict):
            check_for_prohibited_keys(value, current_path)
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                if isinstance(item, dict):
                    check_for_prohibited_keys(item, f"{current_path}[{idx}]")


# -----------------------------------------------------------------------------
# 5. Visual Actions & Spoken Trigger Words
# -----------------------------------------------------------------------------
class VisualActionType(str, Enum):
    """Types of visual actions triggered by speech."""
    APPEAR = "appear"
    ENTER = "enter"
    HIGHLIGHT = "highlight"
    TRANSFORM = "transform"
    UPDATE_VALUE = "update_value"
    PULSE = "pulse"
    EXIT = "exit"
    HOLD = "hold"


class MotionPreset(str, Enum):
    """Semantic motion dynamics preset."""
    REVEAL = "reveal"
    SETTLE = "settle"
    IMPACT = "impact"
    GENTLE = "gentle"


class VisualAction(BaseModel):
    """Action initiated by a spoken trigger word in the narration."""
    model_config = ConfigDict(extra="forbid")

    action_id: str = Field(..., description="Unique action ID within the scene")
    target_node_id: str = Field(..., description="ID of the storyboard node affected by this action")
    action_type: VisualActionType = Field(..., description="Visual action to perform")
    trigger_word: str = Field(
        ...,
        description="Exact verbatim word from the supplied narration that initiates this action",
    )
    trigger_occurrence: int = Field(
        default=1,
        ge=1,
        description="1-indexed occurrence of trigger_word if the word appears multiple times in the narration",
    )
    motion_preset: MotionPreset = Field(
        default=MotionPreset.REVEAL,
        description="Motion physics preset",
    )
    new_value: Any | None = Field(
        default=None,
        description="Optional updated value or state (e.g. new number for update_value action)",
    )
    target_property: str | None = Field(
        default=None,
        description="Target semantic property (e.g. 'number_value', 'style.fill_role')",
    )
    description: str | None = Field(
        default=None,
        description="Human-readable description of the visual intent",
    )


# -----------------------------------------------------------------------------
# 6. Semantic Storyboard Node
# -----------------------------------------------------------------------------
class StoryboardNode(BaseModel):
    """A semantic primitive node in the scene tree."""
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Unique node ID within the scene")
    type: CanonicalCapabilityType = Field(..., description="One of the 13 canonical capability types")
    name: str | None = Field(default=None, description="Optional human-readable name for logging")
    persistence_key: str | None = Field(
        default=None,
        description="Optional persistent ID across scenes for visual continuity",
    )
    persistence_scope: Literal["scene", "cross_scene"] = Field(
        default="scene",
        description="Whether this object persists only in this scene or across scenes",
    )
    macro_zone: MacroScreenZone | None = Field(
        default=None,
        description="Semantic screen zone (used for root nodes in the scene)",
    )
    flow: MicroLayoutFlow | None = Field(
        default=None,
        description="Auto-layout flow configuration (used when type == 'group')",
    )
    style: SemanticStyleIntent = Field(
        default_factory=SemanticStyleIntent,
        description="Semantic design token styles",
    )
    props: dict[str, Any] = Field(
        default_factory=dict,
        description="Semantic properties for this capability type (no raw coordinates or frames)",
    )
    children: list[StoryboardNode] = Field(
        default_factory=list,
        description="Child storyboard nodes (only valid when type == 'group')",
    )

    @model_validator(mode="after")
    def validate_node(self) -> "StoryboardNode":
        # 1. Enforce forbidden high-level capabilities
        if str(self.type) in FORBIDDEN_COMPOSITION_TYPES or self.type.value in FORBIDDEN_COMPOSITION_TYPES:
            raise ValueError(
                f"Cannot use '{self.type}' as capability type. High-level compositions "
                f"({FORBIDDEN_COMPOSITION_TYPES}) must be assembled from primitive groups."
            )

        # 2. Enforce group vs non-group children constraint
        if self.type != CanonicalCapabilityType.GROUP and len(self.children) > 0:
            raise ValueError(
                f"Only 'group' primitives may have children; node '{self.id}' is of type '{self.type.value}'."
            )

        # 3. Check for prohibited downstream keys in props
        check_for_prohibited_keys(self.props, f"node[{self.id}].props")

        return self


# -----------------------------------------------------------------------------
# 7. Semantic Relationships
# -----------------------------------------------------------------------------
class SemanticRelationship(BaseModel):
    """Semantic relationship between visual entities or concepts in a scene.

    Describes conceptual meaning (e.g. 'compared_with', 'contributes_to', 'causes', 'diverges_from', 'leads_to').
    A connector is merely one possible visual representation; the Storyboarder decides
    the appropriate visual manifestation (spatial arrangement, styling, connector, transformation, etc.).
    """
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(..., description="ID of source node, persistence_key, or entity concept")
    relation: str = Field(..., description="Semantic relation type (e.g. 'compared_with', 'contributes_to', 'causes', 'diverges_from', 'leads_to')")
    target_id: str = Field(..., description="ID of target node, persistence_key, or entity concept")
    visual_representation: str | None = Field(
        default=None,
        description="Creative visual manifestation chosen by Storyboarder (e.g. 'side_by_side_contrast', 'stacked_divergence', 'directional_connector', 'state_transformation')",
    )
    description: str | None = Field(
        default=None,
        description="Optional human-readable description of this relationship's storytelling role",
    )


# -----------------------------------------------------------------------------
# 8. Scene Storyboard Specification
# -----------------------------------------------------------------------------
class SceneStoryboardSpec(BaseModel):
    """Storyboard specification for a single scene beat."""
    model_config = ConfigDict(extra="forbid")

    scene_id: str = Field(..., description="Unique scene beat identifier (e.g. 'hook', 'scene_01')")
    idea_id: str | None = Field(default=None, description="Corresponding ScriptVisualStrategy idea_id")
    source_intent_ids: list[str] = Field(
        default_factory=list,
        description="IDs of VisualIntents represented in this scene (a scene may represent multiple VisualIntents)",
    )
    visual_intent: VisualIntent | None = Field(
        default=None,
        description=(
            "Optional complete semantic VisualIntent providing context for what the viewer must understand. "
            "Note: relationship_type is strictly semantic context and NEVER prescribes primitives, "
            "layout, or templates."
        ),
    )
    narration: str = Field(..., description="Exact spoken narration text for this scene")
    macro_zone: MacroScreenZone = Field(
        default=MacroScreenZone.CENTER,
        description="Creative macro screen zone chosen for this scene (not prescribed by relationship_type)",
    )
    root_nodes: list[StoryboardNode] = Field(
        default_factory=list,
        description="Top-level visual nodes in the scene",
    )
    relationships: list[SemanticRelationship] = Field(
        default_factory=list,
        description="Explicit semantic relationships between conceptual entities in this scene",
    )
    actions: list[VisualAction] = Field(
        default_factory=list,
        description="Actions triggered by spoken words within this scene",
    )

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_intent_id(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "intent_id" in data:
                legacy_id = data.pop("intent_id")
                if legacy_id and "source_intent_ids" not in data:
                    data["source_intent_ids"] = [legacy_id] if isinstance(legacy_id, str) else list(legacy_id)
        return data

    @model_validator(mode="after")
    def validate_scene_spec(self) -> "SceneStoryboardSpec":
        # 1. Narration must not be empty
        if not self.narration.strip():
            raise ValueError(f"Scene '{self.scene_id}' narration cannot be empty.")

        # 2. Collect all node IDs in the hierarchy and check for duplicates
        node_ids: set[str] = set()

        def collect_nodes(nodes: list[StoryboardNode]) -> None:
            for node in nodes:
                if node.id in node_ids:
                    raise ValueError(f"Duplicate node ID '{node.id}' in scene '{self.scene_id}'.")
                node_ids.add(node.id)
                collect_nodes(node.children)

        collect_nodes(self.root_nodes)

        # 3. Validate that actions target existing nodes (or cross-scene persistence keys)
        for action in self.actions:
            if action.target_node_id not in node_ids:
                raise ValueError(
                    f"Action '{action.action_id}' targets unknown node ID '{action.target_node_id}' "
                    f"in scene '{self.scene_id}'."
                )

        # 4. Validate trigger words against verbatim narration
        clean_words = extract_narration_words(self.narration)
        word_counts: dict[str, int] = {}
        for w in clean_words:
            word_counts[w.lower()] = word_counts.get(w.lower(), 0) + 1

        for action in self.actions:
            trigger_clean = action.trigger_word.strip().strip(".,!?;:\"'()[]{}").lower()
            if not trigger_clean:
                raise ValueError(
                    f"Action '{action.action_id}' trigger word '{action.trigger_word}' is empty."
                )

            count = word_counts.get(trigger_clean, 0)
            if count == 0:
                raise ValueError(
                    f"Action '{action.action_id}' trigger word '{action.trigger_word}' was not found "
                    f"in the narration for scene '{self.scene_id}': '{self.narration}'"
                )

            if action.trigger_occurrence > count:
                raise ValueError(
                    f"Action '{action.action_id}' trigger word '{action.trigger_word}' requests "
                    f"occurrence {action.trigger_occurrence}, but only appears {count} time(s) "
                    f"in scene '{self.scene_id}' narration."
                )

        return self


# -----------------------------------------------------------------------------
# 8. Project Storyboard Specification
# -----------------------------------------------------------------------------
class ProjectStoryboardSpec(BaseModel):
    """Complete multi-scene storyboard specification for the entire video run."""
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    scenes: list[SceneStoryboardSpec] = Field(
        default_factory=list,
        description="Ordered sequence of scenes covering the full video script",
    )

    @model_validator(mode="after")
    def validate_project(self) -> "ProjectStoryboardSpec":
        scene_ids: set[str] = set()
        for scene in self.scenes:
            if scene.scene_id in scene_ids:
                raise ValueError(f"Duplicate scene_id '{scene.scene_id}' in project storyboard.")
            scene_ids.add(scene.scene_id)
        return self


# -----------------------------------------------------------------------------
# 9. Storyboard Input Context
# -----------------------------------------------------------------------------
class StoryboardInputContext(BaseModel):
    """Context received by the Scene Storyboarder to generate visual specs.

    The Storyboarder receives the COMPLETE VisualIntent (including entities, measurements,
    temporal/causal/comparison context, visual dynamics, and relationship_type).
    relationship_type is strictly semantic context describing WHAT happens conceptually;
    it does NOT dictate or prescribe primitive selection, layout zones, or visual templates.
    The Storyboarder independently reasons about the best visual storytelling form.
    """
    model_config = ConfigDict(extra="forbid")

    visual_intent_artifact: VisualIntentArtifact
    full_script: str
    narrative_plan: NarrativePlan
    verified_facts: list[str] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def extract_narration_words(narration: str) -> list[str]:
    """Tokenizes narration into clean words, preserving currency symbols and numbers."""
    tokens = narration.split()
    words: list[str] = []
    for token in tokens:
        cleaned = token.strip(".,!?;:\"'()[]{}")
        if cleaned:
            words.append(cleaned)
    return words
