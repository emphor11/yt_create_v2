from artifact_store.models import ArtifactLineage, ArtifactRecord, ArtifactTrace, ArtifactTraceNode
from artifact_store.sqlite_store import ArtifactStore


def get_artifact_lineage(store: ArtifactStore, artifact_id: str) -> ArtifactLineage:
    return ArtifactLineage(
        artifact_id=artifact_id,
        parents=store.get_parents(artifact_id),
        children=store.get_children(artifact_id),
    )


def get_artifact_trace(store: ArtifactStore, artifact_id: str) -> ArtifactTrace:
    store.get_artifact(artifact_id)
    return ArtifactTrace(
        artifact_id=artifact_id,
        ancestors=_ancestor_nodes(store, artifact_id),
        descendants=_descendant_nodes(store, artifact_id),
    )


def get_artifact_descendants(store: ArtifactStore, artifact_id: str) -> list[ArtifactRecord]:
    return [
        store.get_artifact(node.artifact_id)
        for node in _descendant_nodes(store, artifact_id)
    ]


def _ancestor_nodes(
    store: ArtifactStore,
    artifact_id: str,
    role_path: str = "",
    depth: int = 0,
    visited: set[str] | None = None,
) -> list[ArtifactTraceNode]:
    visited = visited or set()
    if artifact_id in visited:
        return []
    visited.add(artifact_id)

    nodes: list[ArtifactTraceNode] = []
    for role, parent in store.get_parents(artifact_id).items():
        parent_role_path = f"{role_path}.{role}" if role_path else role
        nodes.append(_trace_node(parent, parent_role_path, depth + 1))
        nodes.extend(
            _ancestor_nodes(
                store,
                parent.id,
                parent_role_path,
                depth + 1,
                visited,
            )
        )
    return nodes


def _descendant_nodes(
    store: ArtifactStore,
    artifact_id: str,
    role_path: str = "",
    depth: int = 0,
    visited: set[str] | None = None,
) -> list[ArtifactTraceNode]:
    visited = visited or set()
    if artifact_id in visited:
        return []
    visited.add(artifact_id)

    nodes: list[ArtifactTraceNode] = []
    for child in store.get_children(artifact_id):
        child_role = _role_for_parent(child, artifact_id)
        child_role_path = f"{role_path}.{child_role}" if role_path else child_role
        nodes.append(_trace_node(child, child_role_path, depth + 1))
        nodes.extend(
            _descendant_nodes(
                store,
                child.id,
                child_role_path,
                depth + 1,
                visited,
            )
        )
    return nodes


def _role_for_parent(child: ArtifactRecord, parent_artifact_id: str) -> str:
    for role, artifact_id in child.parent_artifact_roles_json.items():
        if artifact_id == parent_artifact_id:
            return role
    return child.artifact_type


def _trace_node(
    artifact: ArtifactRecord,
    role_path: str,
    depth: int,
) -> ArtifactTraceNode:
    return ArtifactTraceNode(
        artifact_id=artifact.id,
        artifact_type=artifact.artifact_type,
        status=artifact.status,
        role_path=role_path,
        depth=depth,
    )
