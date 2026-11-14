import requests
from ebooklib import epub

from downloader.domain.novel.models import Chapter, Novel
from downloader.shared.helpers import timer
from downloader.shared.constants import ONE_MINUTE_IN_SECONDS
from downloader.infrastructure.storage import epub_path, delete_epub

COVER_NAME = "cover.jpg"


def cover(slug: str) -> bytes:
    url = f"https://api.devilsect.com/api/novels/{slug}/image"
    data = requests.get(url, timeout=ONE_MINUTE_IN_SECONDS).content
    return data


@timer("EPUB processing")
def generate(novel: Novel, chapters: list[Chapter], job_id: int) -> str:
    if not chapters:
        raise Exception("Must have atleast one chapter")

    first_chapter = chapters[0]
    last_chapter = chapters[-1]

    book = epub.EpubBook()

    cover_bytes = cover(novel.slug)

    book.set_cover(COVER_NAME, cover_bytes)

    book.set_identifier(novel.slug)
    book.set_title(
        f"{novel.title.title()} [Ch.{first_chapter.number} ~ Ch.{last_chapter.number}]"
    )
    book.set_language("en")

    book.add_author(novel.author.title())

    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content="BODY {color: black; background-color: white;}",
    )

    spine = ["nav"]

    for chapter in chapters:
        c1 = epub.EpubHtml(
            title=chapter.title, file_name=f"{chapter.slug}.xhtml", lang="en"
        )
        c1.set_content(
            f"<h2 style='text-align: center;'>[{chapter.number}]. {chapter.title.title()}</h2>{chapter.body}"
        )
        book.add_item(c1)
        spine.append(c1)

    book.add_item(nav_css)

    book.toc = tuple(
        epub.Link(
            f"{chapter.slug}.xhtml", f"[{chapter.number}]. {chapter.title.title()}"
        )
        for chapter in chapters
    )

    book.spine = spine

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub_file = epub_path(
        f"{job_id}.{novel.slug}_ch{first_chapter.number}-ch{last_chapter.number}.epub"
    )

    status = epub.write_epub(epub_file, book)

    if not status:
        delete_epub(epub_file.name)
        raise Exception("Failed to generate epub")

    return epub_file.name
