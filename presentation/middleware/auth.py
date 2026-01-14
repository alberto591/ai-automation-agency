from typing import Any, cast

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from config.settings import settings
from infrastructure.logging import get_logger

logger = get_logger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),  # noqa: B008
) -> dict[str, Any]:
    """
    Verifies the Supabase JWT token.
    Returns the decoded token payload if valid.
    """
    if not settings.SUPABASE_JWT_SECRET:
        # Pydantic validation should catch this, but just in case
        logger.error("MISSING_JWT_SECRET", context={"reason": "SUPABASE_JWT_SECRET not set"})
        raise HTTPException(
            status_code=500, detail="Server Misconfiguration: Missing SUPABASE_JWT_SECRET"
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return cast(dict[str, Any], payload)
    except JWTError as e:
        logger.warning("INVALID_TOKEN", context={"error": str(e)})
        raise HTTPException(status_code=401, detail="Invalid authentication credentials") from e
