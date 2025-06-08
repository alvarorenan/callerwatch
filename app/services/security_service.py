from app.services.ip_checker_service import IPCheckerService
from app.repositories.cache_repository import CacheRepository
from app.models.security import SecurityScore, CallerInfo, RiskLevel
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SecurityService:
    """Main security service orchestrating IP and caller checks"""

    def __init__(self, cache_repo: CacheRepository, ip_checker: IPCheckerService):
        self.cache_repo = cache_repo
        self.ip_checker = ip_checker

    async def check_ip_security(self, ip: str, force_refresh: bool = False) -> SecurityScore:
        """Check IP security with caching"""
        # Check cache first unless force refresh
        if not force_refresh:
            cached_score = await self.cache_repo.get_ip_score(ip)
            if cached_score:
                logger.info(f"Cache hit for IP {ip}")
                return cached_score

        # Perform comprehensive check
        logger.info(f"Performing comprehensive check for IP {ip}")
        score = await self.ip_checker.check_ip_comprehensive(ip)

        # Cache the result
        await self.cache_repo.set_ip_score(score)

        return score

    async def check_caller_info(self, phone_number: str, ip: Optional[str] = None) -> CallerInfo:
        """Check caller information"""
        # This is a placeholder implementation
        # In a real system, you'd query databases, telecom APIs, etc.

        caller_info = CallerInfo(
            phone_number=phone_number,
            risk_level=RiskLevel.LOW,
            reputation_score=0.1
        )

        # If IP is provided, factor it into the risk assessment
        if ip:
            ip_score = await self.check_ip_security(ip)
            if ip_score.reputation.value == "malicious":
                caller_info.risk_level = RiskLevel.HIGH
                caller_info.reputation_score = 0.8
            elif ip_score.reputation.value == "suspicious":
                caller_info.risk_level = RiskLevel.MEDIUM
                caller_info.reputation_score = 0.5

        return caller_info
