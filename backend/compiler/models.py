"""Models and configuration for the deterministic Visual Compiler."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from domain.primitives.spec import PrimitiveTreeSpec
from domain.storyboard import SemanticRelationship


class VisualCompilerError(Exception):
    """Raised when visual compilation fails contract validation or timing resolution."""


@dataclass(frozen=True)
class Rect:
    """A deterministic 2D bounding rectangle in pixel canvas coordinates."""
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2.0

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2.0


class CanvasConfig(BaseModel):
    """Deterministic canvas configuration for 1080p rendering."""
    model_config = ConfigDict(extra="forbid")

    width: int = Field(default=1920, gt=0, description="Canvas width in pixels")
    height: int = Field(default=1080, gt=0, description="Canvas height in pixels")
    fps: int = Field(default=30, gt=0, description="Target animation frame rate")
    safe_margin_x: float = Field(default=120.0, ge=0, description="Horizontal title-safe margin")
    safe_margin_y: float = Field(default=80.0, ge=0, description="Vertical title-safe margin")

    @property
    def safe_rect(self) -> Rect:
        """Returns the safe rectangular boundary inside the outer margin."""
        return Rect(
            x=self.safe_margin_x,
            y=self.safe_margin_y,
            width=float(self.width - 2 * self.safe_margin_x),
            height=float(self.height - 2 * self.safe_margin_y),
        )

    @property
    def full_rect(self) -> Rect:
        """Returns the full canvas boundary."""
        return Rect(x=0.0, y=0.0, width=float(self.width), height=float(self.height))


class CompiledSceneResult(BaseModel):
    """Result of compiling a single storyboard scene beat into a PrimitiveTreeSpec."""
    model_config = ConfigDict(extra="forbid")

    scene_id: str
    duration_frames: int
    duration_seconds: float
    tree_spec: PrimitiveTreeSpec
    relationships: list[SemanticRelationship] = Field(default_factory=list)
    persistent_keys: dict[str, str] = Field(default_factory=dict)


class CompiledProjectResult(BaseModel):
    """Result of compiling an entire ProjectStoryboardSpec against a VoiceTrack."""
    model_config = ConfigDict(extra="forbid")

    canvas_config: CanvasConfig
    scenes: list[CompiledSceneResult] = Field(default_factory=list)
    scene_trees: dict[str, PrimitiveTreeSpec] = Field(default_factory=dict)
    total_duration_frames: int = 0
    total_duration_seconds: float = 0.0
