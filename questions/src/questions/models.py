from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from database import Base
from my_type_notation import intpk


class Question(Base):
    __tablename__ = "question"

    id: Mapped[intpk]
    initials: Mapped[str]
    place: Mapped[str]
    position: Mapped[str]
    text: Mapped[str]
    category: Mapped["Category"] = relationship(back_populates="questions", uselist=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))


class Category(Base):
    __tablename__ = "category"

    id: Mapped[intpk]
    name: Mapped[str]
    questions: Mapped[List[Question]] = relationship(back_populates="category", uselist=True)
