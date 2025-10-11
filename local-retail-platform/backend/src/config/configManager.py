"""Configuration Manager for Local Retail Platform.

This module provides centralized configuration management using Pydantic
for validation and type safety.
"""

from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class BackendConfig(BaseSettings):
    """Backend application configuration."""

    debug: bool = False
    secret_key: str
    allowed_hosts: List[str] = Field(default_factory=lambda: ["localhost"])
    cors_allowed_origins: List[str] = Field(default_factory=list)

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Ensure secret key is not the default insecure one in production."""
        # Get debug value from the data being validated
        debug_mode = info.data.get("debug", False)

        if not debug_mode and "insecure" in v.lower():
            raise ValueError("Insecure secret key detected in production mode")
        return v


class DatabaseConfig(BaseSettings):
    """Database configuration."""

    engine: str = "django.db.backends.sqlite3"
    name: str = "db.sqlite3"
    user: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None


class JWTConfig(BaseSettings):
    """JWT authentication configuration."""

    access_token_lifetime_minutes: int = 60
    refresh_token_lifetime_days: int = 7
    algorithm: str = "HS256"


class GeoConfig(BaseSettings):
    """Geolocation business rules."""

    default_radius_km: int = 150
    max_radius_km: int = 500


class LoyaltyConfig(BaseSettings):
    """Loyalty token system configuration."""

    token_value_euro: float = 1.0
    purchase_threshold_euro: float = 100.0


class SubscriptionConfig(BaseSettings):
    """Merchant subscription tiers."""

    free_tier_commission_percent: float = 7.3
    premium_tier_commission_percent: float = 3.1
    premium_monthly_fee_euro: float = 299.0


class BusinessConfig(BaseSettings):
    """Business rules configuration."""

    geo: GeoConfig
    loyalty: LoyaltyConfig
    subscription: SubscriptionConfig


class StripeConfig(BaseSettings):
    """Stripe payment provider configuration."""

    enabled: bool = False
    public_key: str = ""
    secret_key: str = ""


class PayPalConfig(BaseSettings):
    """PayPal payment provider configuration."""

    enabled: bool = False
    client_id: str = ""
    client_secret: str = ""


class PaymentsConfig(BaseSettings):
    """Payment providers configuration."""

    stripe: StripeConfig
    paypal: PayPalConfig


class EmailConfig(BaseSettings):
    """Email configuration."""

    backend: str = "django.core.mail.backends.console.EmailBackend"
    from_email: str = "noreply@localretail.com"
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = True


class LoggingConfig(BaseSettings):
    """Logging configuration."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class RateLimitingConfig(BaseSettings):
    """API rate limiting configuration."""

    enabled: bool = False
    default_throttle_rate: str = "100/hour"


class AppConfig(BaseSettings):
    """Main application configuration."""

    backend: BackendConfig
    database: DatabaseConfig
    jwt: JWTConfig
    business: BusinessConfig
    payments: PaymentsConfig
    email: EmailConfig
    logging: LoggingConfig
    rate_limiting: RateLimitingConfig


class ConfigManager:
    """Singleton configuration manager."""

    _instance: Optional["ConfigManager"] = None
    _config: Optional[AppConfig] = None

    def __new__(cls) -> "ConfigManager":
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize configuration manager."""
        if self._config is None:
            self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        config_path = Path(__file__).parent.parent.parent / "config.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        # Parse nested configurations
        self._config = AppConfig(
            backend=BackendConfig(**config_data.get("backend", {})),
            database=DatabaseConfig(**config_data.get("database", {})),
            jwt=JWTConfig(**config_data.get("jwt", {})),
            business=BusinessConfig(
                geo=GeoConfig(**config_data.get("business", {}).get("geo", {})),
                loyalty=LoyaltyConfig(
                    **config_data.get("business", {}).get("loyalty", {})
                ),
                subscription=SubscriptionConfig(
                    **config_data.get("business", {}).get("subscription", {})
                ),
            ),
            payments=PaymentsConfig(
                stripe=StripeConfig(
                    **config_data.get("payments", {}).get("stripe", {})
                ),
                paypal=PayPalConfig(
                    **config_data.get("payments", {}).get("paypal", {})
                ),
            ),
            email=EmailConfig(**config_data.get("email", {})),
            logging=LoggingConfig(**config_data.get("logging", {})),
            rate_limiting=RateLimitingConfig(**config_data.get("rate_limiting", {})),
        )

    @property
    def config(self) -> AppConfig:
        """Get the application configuration."""
        if self._config is None:
            self._load_config()
        assert self._config is not None
        return self._config

    def reload(self) -> None:
        """Reload configuration from file."""
        self._config = None
        self._load_config()


# Global config instance
config_manager = ConfigManager()