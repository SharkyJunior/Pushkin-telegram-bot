from sqlalchemy.orm import Mapped
from sqlalchemy import String, Text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import mapped_column


class BasicMixin(object):

    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
