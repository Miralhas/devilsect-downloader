from sqlmodel import Session, select, col

from downloader.domain.novel.models import Novel, Chapter
from downloader.infrastructure.database import engine


def select_novel_by_slug(slug: str) -> Novel:
    with Session(engine) as session:
        statement = select(Novel).where(Novel.slug == slug)
        result = session.exec(statement)
        return result.first()


def select_chapters_from_novel_id(id: int, start: int, end: int, exclude: list[str] = []) -> list[Chapter]:
    with Session(engine) as session:
        statement = (
            select(Chapter, Novel)
            .join(Novel, isouter=True)
            .where(Novel.id == id)
            .where(col(Chapter.number).between(start, end))
            .where(col(Chapter.number).not_in(exclude))
            .order_by(col(Chapter.number))
        )
        results = session.exec(statement)
        return [chapter for chapter, novel in results]
