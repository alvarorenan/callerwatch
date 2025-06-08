from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, status, Depends
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.models.auth import TokenPayload

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class SecurityService:

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_jwt_token(data: dict) -> str:
        """Create JWT token"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + \
            timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        })
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def decode_jwt_token(token: str) -> TokenPayload:
        """Decode JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[
                                 settings.JWT_ALGORITHM])
            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenPayload:
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    return SecurityService.decode_jwt_token(credentials.credentials)
