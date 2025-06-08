from fastapi import APIRouter, HTTPException, status
from app.models.auth import UserLogin, Token
from app.core.security import SecurityService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Authenticate user and return JWT token"""
    try:
        # Simple authentication - replace with real user validation
        if credentials.username == "admin" and credentials.password == "admin123":
            token = SecurityService.create_jwt_token({
                "sub": credentials.username,
                "role": "admin"
            })

            return Token(
                access_token=token,
                expires_in=24 * 3600  # 24 hours
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )


@router.post("/refresh")
async def refresh_token():
    """Refresh JWT token"""
    # Implement token refresh logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not implemented"
    )
