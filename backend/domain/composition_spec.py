"""
CompositionSpec — the resolver-output model.

After CompositionResolver processes a CompositionBeat, it returns a
CompositionSpec that wraps the Remotion-ready ComponentSpec along with
the original composition metadata for debugging.

This is an internal model used by CompositionAssemblyEngine; it does not
appear in artifacts or the public API.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CompositionSpec(BaseModel):
    """
    Resolved, renderer-ready specification of a composition scene.

    Maps one-to-one with a ComponentSpec in the RenderSpec, but retains
    composition-level context (composition_id, asset_requirement) for the
    assembly engine to use when wiring assets.
    """

    composition_id: str = Field(
        description="The composition that was selected, e.g. 'metric_hero'."
    )
    component_id: str = Field(
        description="The Remotion component that renders this composition, e.g. 'MetricHero'."
    )
    props: dict[str, Any] = Field(
        default_factory=dict,
        description="camelCase prop dict for the Remotion component.",
    )
    asset_requirement: str = Field(
        default="none",
        description="Passed through from CompositionBeat for asset resolution.",
    )
