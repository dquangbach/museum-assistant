import secrets

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

admin_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)


def require_admin(request: Request, key: str | None = Security(admin_header)) -> None:
    expected = request.app.state.settings.admin_api_key
    if not expected:
        raise HTTPException(503, "Admin API is disabled; configure ADMIN_API_KEY")
    if key is None or not secrets.compare_digest(key.encode(), expected.encode()):
        raise HTTPException(401, "Invalid admin API key")
