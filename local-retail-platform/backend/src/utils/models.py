"""Shared Pydantic models for data validation across the platform."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class UserRole(str, Enum):
    """User role enumeration."""

    MERCHANT = "merchant"
    CUSTOMER = "customer"
    ADMIN = "admin"


class SubscriptionTier(str, Enum):
    """Merchant subscription tier."""

    FREE = "free"
    PREMIUM = "premium"


class OrderStatus(str, Enum):
    """Order status enumeration."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    """Payment status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    """Payment method types."""

    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    LOYALTY_TOKEN = "loyalty_token"


class NotificationType(str, Enum):
    """Notification type enumeration."""

    ORDER_PLACED = "order_placed"
    ORDER_SHIPPED = "order_shipped"
    ORDER_DELIVERED = "order_delivered"
    LOW_STOCK = "low_stock"
    RESTOCK_SUGGESTION = "restock_suggestion"
    NEW_CUSTOMER = "new_customer"
    PAYMENT_RECEIVED = "payment_received"


class GeoLocation(BaseModel):
    """Geographic location model."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "DE"

    @field_validator("latitude", "longitude")
    @classmethod
    def validate_coordinates(cls, v: float) -> float:
        """Validate coordinate precision."""
        return round(v, 6)  # Limit to ~0.1m precision


class MoneyAmount(BaseModel):
    """Money amount with currency."""

    amount: Decimal = Field(..., ge=0, decimal_places=2)
    currency: str = Field(default="EUR", pattern="^[A-Z]{3}$")

    def __add__(self, other: "MoneyAmount") -> "MoneyAmount":
        """Add two money amounts."""
        if self.currency != other.currency:
            raise ValueError("Cannot add amounts with different currencies")
        return MoneyAmount(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: "MoneyAmount") -> "MoneyAmount":
        """Subtract two money amounts."""
        if self.currency != other.currency:
            raise ValueError("Cannot subtract amounts with different currencies")
        return MoneyAmount(amount=self.amount - other.amount, currency=self.currency)

    def __mul__(self, multiplier: float) -> "MoneyAmount":
        """Multiply money amount by a scalar."""
        return MoneyAmount(amount=self.amount * Decimal(str(multiplier)), currency=self.currency)


class TimeStampedModel(BaseModel):
    """Base model with timestamp fields."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.page_size


class SearchRadius(BaseModel):
    """Geographic search radius parameters."""

    center: GeoLocation
    radius_km: int = Field(default=150, ge=1, le=500)

    @field_validator("radius_km")
    @classmethod
    def validate_radius(cls, v: int) -> int:
        """Ensure radius is within business limits."""
        from ..config.configManager import config_manager

        max_radius = config_manager.config.business.geo.max_radius_km
        if v > max_radius:
            raise ValueError(f"Radius cannot exceed {max_radius} km")
        return v


class LoyaltyTokenCalculation(BaseModel):
    """Loyalty token calculation result."""

    purchase_amount: MoneyAmount
    tokens_earned: int
    token_value: MoneyAmount

    @classmethod
    def calculate(cls, purchase_amount: MoneyAmount) -> "LoyaltyTokenCalculation":
        """Calculate loyalty tokens from purchase amount."""
        from ..config.configManager import config_manager

        config = config_manager.config.business.loyalty
        threshold = Decimal(str(config.purchase_threshold_euro))
        token_value = Decimal(str(config.token_value_euro))

        tokens = int(purchase_amount.amount // threshold)
        value = MoneyAmount(amount=tokens * token_value, currency=purchase_amount.currency)

        return cls(
            purchase_amount=purchase_amount,
            tokens_earned=tokens,
            token_value=value,
        )