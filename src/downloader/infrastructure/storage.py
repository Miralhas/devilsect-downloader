from pathlib import Path
from downloader.config.settings import env

def epub_path(filename: str) -> Path:
    return Path(env.OUTPUT_FOLDER) / filename


def delete_epub(filename: str) -> bool:
    path = epub_path(filename)
    if not path.exists():
        return False

    path.unlink()
    return True