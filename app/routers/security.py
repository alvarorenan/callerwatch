from fastapi import APIRouter, Depends, HTTPException, status
from app.models.security import IPCheckRequest, CallerCheckRequest, SecurityScore, CallerInfo, ApiResponse
from app.models.auth import TokenPayload
from app.core.security import get_current_user
from app.services.security_service import SecurityService
from app.dependencies import get_security_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/security", tags=["Security"])


@router.post("/check/ip", response_model=ApiResponse)
async def check_ip_security(
    request: IPCheckRequest,
    security_service: SecurityService = Depends(get_security_service),
    current_user: TokenPayload = Depends(get_current_user)
):
    """Check IP security reputation"""
    try:
        score = await security_service.check_ip_security(
            str(request.ip),
            force_refresh=False
        )

        logger.info(
            f"IP {request.ip} checked by user {current_user.sub} - Score: {score.score}")

        return ApiResponse(
            success=True,
            data=score.model_dump(),
            message="IP check completed successfully"
        )

    except Exception as e:
        logger.error(f"Error checking IP {request.ip}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during IP check"
        )


@router.post("/check/caller", response_model=ApiResponse)
async def check_caller_info(
    request: CallerCheckRequest,
    security_service: SecurityService = Depends(get_security_service),
    current_user: TokenPayload = Depends(get_current_user)
):
    """Check caller information and reputation"""
    try:
        caller_info = await security_service.check_caller_info(
            request.phone_number,
            str(request.ip) if request.ip else None
        )

        logger.info(
            f"Caller {request.phone_number} checked by user {current_user.sub}")

        return ApiResponse(
            success=True,
            data=caller_info.model_dump(),
            message="Caller check completed successfully"
        )

    except Exception as e:
        logger.error(f"Error checking caller {request.phone_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during caller check"
        )


@router.get("/stats", response_model=ApiResponse)
async def get_security_stats(
    current_user: TokenPayload = Depends(get_current_user)
):
    """Get security statistics"""
    try:
        # Placeholder for real statistics
        stats = {
            "total_ips_checked": 1000,
            "total_callers_checked": 500,
            "cache_hit_rate": 0.85,
            "avg_response_time": 150.5,
            "top_threats": [],
            "recent_activity": []
        }

        return ApiResponse(
            success=True,
            data=stats,
            message="Statistics retrieved successfully"
        )

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error getting statistics"
        )
