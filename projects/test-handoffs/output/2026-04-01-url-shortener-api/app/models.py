from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    links: Mapped[list["Link"]] = relationship("Link", back_populates="owner")


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(12), unique=True, index=True, nullable=False)
    original_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    # Null means the link was created anonymously
    owner_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    owner: Mapped["User | None"] = relationship("User", back_populates="links")
    clicks: Mapped[list["Click"]] = relationship("Click", back_populates="link", cascade="all, delete-orphan")


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    link_id: Mapped[int] = mapped_column(Integer, ForeignKey("links.id"), nullable=False)
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    referrer: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)

    link: Mapped["Link"] = relationship("Link", back_populates="clicks")
