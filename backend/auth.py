from fastapi import Header, HTTPException

from backend.services.supabase_service import SupabaseService

_service = None


def _get_service() -> SupabaseService:
    global _service

    if _service is None:
        _service = SupabaseService()

    return _service


def get_current_user_id(
    authorization: str | None = Header(default=None)
) -> str:
    """Return the Supabase user id that owns the bearer token.

    The user is always taken from the verified login token, never from
    the request body, so one user cannot read or write another user's data.
    """
    if (
        not authorization
        or not authorization.lower().startswith("bearer ")
    ):
        raise HTTPException(
            status_code=401,
            detail="Missing bearer token."
        )

    token = authorization[7:].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing bearer token."
        )

    try:
        response = _get_service().client.auth.get_user(token)
        user = response.user if response else None
    except Exception:
        user = None

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    return user.id
