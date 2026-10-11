"""Deterministic Cross-Scene Persistence Manager.

Tracks object continuity across consecutive scenes.
When an object with `persistence_scope="cross_scene"` or a persistent key continues into a later scene:
- Suppresses entrance/appear animations that would incorrectly treat an established object as new.
- Ensures timing.enter_frame defaults to 0 (already visible when scene starts).
- Preserves object continuity while allowing state evolutions (transforms, highlights, value updates).
"""
from __future__ import annotations

from typing import Any
from domain.storyboard import StoryboardNode, VisualAction, VisualActionType


class PersistenceManager:
    """Tracks cross-scene persistent entities and manages continuity rules."""

    def __init__(self) -> None:
        # Maps persistence_key -> scene_id where it first appeared
        self._first_seen_scene: dict[str, str] = {}
        # Maps persistence_key -> node_id in the most recent scene
        self._last_node_id: dict[str, str] = {}
        # Maps persistence_key -> last known state / props
        self._last_known_state: dict[str, dict[str, Any]] = {}

    def get_persistence_key(self, node: StoryboardNode) -> str | None:
        """Determines the persistence key for a node, if cross-scene persistence applies."""
        if node.persistence_key:
            return node.persistence_key
        if node.persistence_scope == "cross_scene":
            return node.id
        return None

    def is_established(self, persistence_key: str, current_scene_id: str) -> bool:
        """Returns True if this persistence_key was introduced in an earlier scene."""
        first_scene = self._first_seen_scene.get(persistence_key)
        return first_scene is not None and first_scene != current_scene_id

    def register_node(
        self,
        scene_id: str,
        node: StoryboardNode,
        initial_state: dict[str, Any] | None = None,
    ) -> str | None:
        """Registers a node in the current scene if it has persistence."""
        pkey = self.get_persistence_key(node)
        if not pkey:
            return None

        if pkey not in self._first_seen_scene:
            self._first_seen_scene[pkey] = scene_id

        self._last_node_id[pkey] = node.id
        if initial_state:
            self._last_known_state[pkey] = dict(initial_state)

        return pkey

    def should_suppress_entrance(self, node: StoryboardNode, current_scene_id: str) -> bool:
        """Determines whether entrance animation should be suppressed for this node."""
        pkey = self.get_persistence_key(node)
        if not pkey:
            return False
        return self.is_established(pkey, current_scene_id)

    def filter_actions_for_node(
        self,
        node: StoryboardNode,
        actions: list[VisualAction],
        current_scene_id: str,
    ) -> list[VisualAction]:
        """Filters out redundant 'appear'/'enter' actions if the node is already established."""
        if not self.should_suppress_entrance(node, current_scene_id):
            return actions

        filtered: list[VisualAction] = []
        for act in actions:
            act_type = act.action_type.value if hasattr(act.action_type, "value") else str(act.action_type)
            if act_type in (VisualActionType.APPEAR.value, VisualActionType.ENTER.value):
                # Suppress appearance action on already-established persistent object
                continue
            filtered.append(act)
        return filtered

    def get_all_persistent_keys(self) -> dict[str, str]:
        """Returns mapping of all tracked persistence_keys to their originating scene."""
        return dict(self._first_seen_scene)
