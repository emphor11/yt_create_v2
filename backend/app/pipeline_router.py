from domain.pipeline_stage import PipelineStage
from app.stage_handlers.base_handler import BaseStageHandler


class PipelineRouter:
    def __init__(self, handlers: dict[PipelineStage, BaseStageHandler]):
        self._handlers = handlers

    def execute(self, stage: PipelineStage, project_id: str, run_id: str):
        from app.pipeline_service import PipelineServiceError

        handler = self._handlers.get(stage)
        if handler is None:
            raise PipelineServiceError(f"Stage '{stage.value}' is not implemented.")
        return handler.run(project_id, run_id)
