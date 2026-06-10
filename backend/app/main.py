from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import artifacts, media, pipeline, projects


def create_app() -> FastAPI:
    app = FastAPI(title="YTCreate V2 API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(projects.router)
    app.include_router(artifacts.router)
    app.include_router(pipeline.router)
    app.include_router(media.router)

    return app


app = create_app()
