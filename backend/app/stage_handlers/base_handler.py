from typing import Protocol
from artifact_store.models import ArtifactRecord


class BaseStageHandler(Protocol):
    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        """Run this specific pipeline stage."""
