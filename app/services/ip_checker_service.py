from abc import ABC, abstractmethod
from typing import Dict, Any, List
import httpx
import asyncio
from app.core.config import settings
from app.models.security import SecurityScore, ReputationLevel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class IPCheckProvider(ABC):
    """Abstract base class for IP checking providers"""

    @abstractmethod
    async def check_ip(self, ip: str) -> Dict[str, Any]:
        """Check IP reputation"""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider name"""
        pass


class AbuseIPDBProvider(IPCheckProvider):
    """AbuseIPDB provider implementation"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.abuseipdb.com/api/v2"

    @property
    def provider_name(self) -> str:
        return "abuseipdb"

    async def check_ip(self, ip: str) -> Dict[str, Any]:
        """Check IP using AbuseIPDB"""
        if not self.api_key:
            logger.warning("AbuseIPDB API key not configured")
            return {"score": 0, "error": "API key not configured"}

        logger.info(f"Checking IP {ip} with AbuseIPDB...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Key": self.api_key,
                    "Accept": "application/json"
                }
                params = {
                    "ipAddress": ip,
                    "maxAgeInDays": 90,
                    "verbose": ""
                }

                logger.info(f"Making request to AbuseIPDB for {ip}")
                response = await client.get(
                    f"{self.base_url}/check",
                    headers=headers,
                    params=params
                )

                logger.info(f"AbuseIPDB response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"AbuseIPDB full response: {data}")
                    
                    ip_data = data.get("data", {})
                    # 🔥 CORREÇÃO: usar abuseConfidenceScore em vez de abuseConfidencePercentage
                    score = ip_data.get("abuseConfidenceScore", 0)  # Era abuseConfidencePercentage
                    
                    logger.info(f"AbuseIPDB score for {ip}: {score}")
                    logger.info(f"Usage type: {ip_data.get('usageType')}")
                    logger.info(f"Country: {ip_data.get('countryCode')}")
                    logger.info(f"Total reports: {ip_data.get('totalReports', 0)}")
                    
                    return {
                        "score": score,
                        "usage_type": ip_data.get("usageType"),
                        "country": ip_data.get("countryCode"),
                        "reports": ip_data.get("totalReports", 0),
                        "last_reported": ip_data.get("lastReportedAt"),
                        "is_tor": ip_data.get("isTor", False),
                        "is_whitelisted": ip_data.get("isWhitelisted", False),
                        "isp": ip_data.get("isp"),
                        "domain": ip_data.get("domain")
                    }
                else:
                    logger.error(f"AbuseIPDB API error: {response.status_code} - {response.text}")
                    return {"score": 0, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"AbuseIPDB check failed for {ip}: {e}")
            return {"score": 0, "error": str(e)}


class IPCheckerService:
    """Service for checking IP reputation using multiple providers"""

    def __init__(self):
        self.providers: List[IPCheckProvider] = []
        self._init_providers()

    def _init_providers(self):
        """Initialize available providers"""
        logger.info(f"Initializing providers...")
        logger.info(f"AbuseIPDB API key configured: {bool(settings.ABUSEIPDB_API_KEY)}")
        
        if settings.ABUSEIPDB_API_KEY:
            self.providers.append(
                AbuseIPDBProvider(settings.ABUSEIPDB_API_KEY))
            logger.info("AbuseIPDB provider added")
        else:
            logger.warning("AbuseIPDB API key not found in settings")

        logger.info(f"Total providers initialized: {len(self.providers)}")

    async def check_ip_comprehensive(self, ip: str) -> SecurityScore:
        """Perform comprehensive IP check using all providers"""
        if not self.providers:
            return SecurityScore(
                ip=ip,
                score=0,
                reputation=ReputationLevel.SAFE,
                sources=[],
                last_updated=datetime.utcnow(),
                confidence=0.0
            )

        # Run all providers concurrently
        tasks = [provider.check_ip(ip) for provider in self.providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        total_score = 0
        valid_results = 0
        sources = []
        details = {}

        for i, result in enumerate(results):
            if isinstance(result, dict) and not result.get("error"):
                provider_name = self.providers[i].provider_name
                score = result.get("score", 0)

                total_score += score
                valid_results += 1
                sources.append(provider_name)
                details[provider_name] = result

        # Calculate final score and reputation
        if valid_results > 0:
            final_score = min(total_score // valid_results, 100)
            confidence = min(valid_results / len(self.providers), 1.0)
        else:
            final_score = 0
            confidence = 0.0

        reputation = self._calculate_reputation(final_score)

        return SecurityScore(
            ip=ip,
            score=final_score,
            reputation=reputation,
            sources=sources,
            last_updated=datetime.utcnow(),
            details=details,
            confidence=confidence
        )

    def _calculate_reputation(self, score: int) -> ReputationLevel:
        """Calculate reputation based on score with more realistic thresholds"""
        if score >= 75:  # Score muito alto = definitivamente malicioso
            return ReputationLevel.MALICIOUS
        elif score >= 25:  # Score médio = suspeito  
            return ReputationLevel.SUSPICIOUS
        elif score >= 5:   # Score baixo = suspeito leve
            return ReputationLevel.SUSPICIOUS
        else:  # Score 0-4 = seguro
            return ReputationLevel.SAFE
