import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests
from google.oauth2 import id_token

load_dotenv()

bearer_scheme = HTTPBearer(auto_error=False)


def get_allowed_admin_emails() -> set[str]:
    raw = os.getenv("ALLOWED_ADMIN_EMAILS", "")

    return {
        email.strip().lower()
        for email in raw.split(",")
        if email.strip()
    }


def verify_google_admin_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    """
    Verifies a Google ID token passed as:

    Authorization: Bearer <GOOGLE_ID_TOKEN>

    Only emails listed in ALLOWED_ADMIN_EMAILS are allowed.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header.",
        )

    token = credentials.credentials

    try:
        claims = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            audience=os.getenv("GOOGLE_CLIENT_ID"),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token.",
        ) from exc

    email = claims.get("email", "").lower()
    allowed_emails = get_allowed_admin_emails()

    if email not in allowed_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated Google account is not authorized.",
        )

    return claims