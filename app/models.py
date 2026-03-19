from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Message(Base):
    """Stores mock messages for the /message/{id} endpoint."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
