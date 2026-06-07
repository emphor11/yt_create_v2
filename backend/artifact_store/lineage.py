from artifact_store.models import ArtifactLineage
from artifact_store.sqlite_store import ArtifactStore


def get_artifact_lineage(store: ArtifactStore, artifact_id: str) -> ArtifactLineage:
    return ArtifactLineage(
        artifact_id=artifact_id,
        parents=store.get_parents(artifact_id),
        children=store.get_children(artifact_id),
    )

