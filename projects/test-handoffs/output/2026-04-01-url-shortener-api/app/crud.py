from sqlalchemy.orm import Session
from . import models
from .utils import generate_code


def get_link_by_code(db: Session, code: str) -> models.Link | None:
    return db.query(models.Link).filter(models.Link.code == code).first()


def create_link(db: Session, original_url: str, custom_code: str | None = None) -> models.Link:
    code = custom_code or _unique_code(db)
    link = models.Link(code=code, original_url=original_url)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def record_click(db: Session, link: models.Link, referrer: str | None, user_agent: str | None) -> None:
    click = models.Click(link_id=link.id, referrer=referrer, user_agent=user_agent)
    db.add(click)
    db.commit()


def delete_link(db: Session, link: models.Link) -> None:
    db.delete(link)
    db.commit()


def _unique_code(db: Session, attempts: int = 5) -> str:
    for _ in range(attempts):
        code = generate_code()
        if not get_link_by_code(db, code):
            return code
    raise RuntimeError("Failed to generate a unique short code after multiple attempts")
