from pathlib import Path, PurePosixPath


class MediaStorageError(Exception):
    """Raised when a media storage key is unsafe or invalid."""


class LocalMediaStorage:
    def __init__(self, root_path: str | Path):
        # Render providers may change their working directory. Keep every
        # storage path absolute so the artifact path and renderer path cannot
        # diverge.
        self.root_path = Path(root_path).expanduser().resolve()

    def path_for_key(self, storage_key: str) -> Path:
        key_path = PurePosixPath(storage_key)
        if key_path.is_absolute() or ".." in key_path.parts:
            raise MediaStorageError("Storage key must be a safe relative path.")
        return self.root_path.joinpath(*key_path.parts)

    def ensure_parent(self, storage_key: str) -> Path:
        output_path = self.path_for_key(storage_key)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path
