from __future__ import annotations

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from .crud import get_user


SESSION_USER_KEY = "user_id"


def current_user(request: Request, db: Session):
    user_id = request.session.get(SESSION_USER_KEY)
    if not user_id:
        return None
    return get_user(db, user_id)


def require_user(request: Request, db: Session):
    user = current_user(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    return user


def sign_in(request: Request, user_id: str) -> None:
    request.session[SESSION_USER_KEY] = user_id


def sign_out(request: Request) -> None:
    request.session.pop(SESSION_USER_KEY, None)

