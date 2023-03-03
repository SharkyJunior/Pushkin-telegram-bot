from sqlalchemy import create_engine, String, Text, ForeignKey
from typing import List
from typing import Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
# from sqlalchemy.orm import sessionmaker

from models_core import BasicMixin


class Base(DeclarativeBase):
    pass


class Hall(Base, BasicMixin):
    __tablename__ = 'halls'

    halls: Mapped[List['Exhibit']] = relationship(
        back_populates='hall', cascade='all, delete-orphan',
    )


class Author(Base, BasicMixin):
    __tablename__ = 'authors'

    author: Mapped[List['Exhibit']] = relationship(
        back_populates='author', cascade='all, delete-orphan',
    )


class Collection(Base, BasicMixin):
    __tablename__ = 'collections'

    collections: Mapped[List['Exhibit']] = relationship(
        back_populates='collection', cascade='all, delete-orphan',
    )


class Link(Base):
    __tablename__ = 'links'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    comment: Mapped[str] = mapped_column(Text)
    exhibit_id: Mapped[int] = mapped_column(ForeignKey("exhibits.id"))


class Exhibit(Base, BasicMixin):
    __tablename__ = 'exhibits'

    inv_number: Mapped[int]
    theme: Mapped[Optional[str]]
    year: Mapped[Optional[int]]
    period: Mapped[Optional[str]]
    scan: Mapped[Optional[str]]
    technique: Mapped[Optional[str]]
    size: Mapped[Optional[str]]
    notes: Mapped[Optional[str]]
    type: Mapped[Optional[str]]
    country: Mapped[Optional[str]]
    specificity: Mapped[Optional[str]]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    hall_id: Mapped[int] = mapped_column(ForeignKey("halls.id"))
    collection_id: Mapped[int] = mapped_column(ForeignKey("collections.id"))
    links: Mapped[List['Link']] = relationship(
        back_populates='exhibit', cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f'Exhibit(id={self.id!r}, name={self.name!r})'


db = create_engine(
    'postgresql+psycopg2://:@localhost:5432/sharkyjunior', echo=True)

Base.metadata.create_all(db)


# with db.connect() as conn:
#     # Create
#     film_table.create(db)
#     print(meta.tables)
#     print(film_table)
#     insert_statement = insert(film_table).values(
#         title='Doctor Strange', director='Scott Derrickson', year='2016')
#     print(meta.tables)
#     conn.execute(insert_statement)

#     # Read
#     select_statement = select(film_table)
#     result_set = conn.execute(select_statement)
#     for r in result_set:
#         print(r)
