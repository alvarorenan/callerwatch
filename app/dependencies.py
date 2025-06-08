from app.services.security_service import SecurityService
from app.services.ip_checker_service import IPCheckerService
from app.repositories.cache_repository import CacheRepository

# Global instances (consider using dependency injection container in production)
_cache_repo = None
_ip_checker = None
_security_service = None


async def get_cache_repository() -> CacheRepository:
    """Get cache repository instance"""
    global _cache_repo
    if _cache_repo is None:
        _cache_repo = CacheRepository()
        await _cache_repo.connect()
    return _cache_repo


async def get_ip_checker_service() -> IPCheckerService:
    """Get IP checker service instance"""
    global _ip_checker
    if _ip_checker is None:
        _ip_checker = IPCheckerService()
    return _ip_checker


async def get_security_service() -> SecurityService:
    """Get security service instance"""
    global _security_service
    if _security_service is None:
        cache_repo = await get_cache_repository()
        ip_checker = await get_ip_checker_service()
        _security_service = SecurityService(cache_repo, ip_checker)
    return _security_service
