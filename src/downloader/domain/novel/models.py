from sqlmodel import Field, SQLModel


class Novel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slug: str
    title: str
    author: str


class Chapter(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    number: int
    title: str
    body: str
    slug: str

    novel_id: int | None = Field(default=None, foreign_key="novel.id")
