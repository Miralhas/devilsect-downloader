from downloader.domain.novel.repositories import (
    select_chapters_from_novel_id,
    select_novel_by_slug,
)
from downloader.domain.novel.models import Chapter, Novel


def get_novel_by_slug_or_exception(slug: str) -> Novel:
    novel = select_novel_by_slug(slug)

    if not novel:
        raise Exception(f"Failed to get novel with slug: {slug}")

    return novel


def get_novel_chapters(novelId: int, start: int, end: int, exclude: list[str] = []) -> list[Chapter]:
    chapters = select_chapters_from_novel_id(novelId, start, end, exclude)
    return chapters
