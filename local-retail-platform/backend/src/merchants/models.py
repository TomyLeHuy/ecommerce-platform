"""Merchant models for the Local Retail Platform."""

from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class MerchantProfile(models.Model):
    """Extended profile for merchant users."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="merchant_profile",
        verbose_name=_("User"),
    )
    company_name = models.CharField(
        max_length=255,
        verbose_name=_("Company Name"),
        help_text=_("Official business name"),
    )
    tax_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Tax ID"),
        help_text=_("Steuernummer or USt-IdNr."),
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_("Phone Number"),
    )

    # Business Address
    street_address = models.CharField(max_length=255, verbose_name=_("Street Address"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    postal_code = models.CharField(max_length=10, verbose_name=_("Postal Code"))
    country = models.CharField(
        max_length=2,
        default="DE",
        verbose_name=_("Country Code"),
    )

    # Geographic coordinates for location-based search
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        verbose_name=_("Latitude"),
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        verbose_name=_("Longitude"),
    )

    # DATEV Integration
    datev_client_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("DATEV Client ID"),
        help_text=_("For accounting integration"),
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Verified"),
        help_text=_("Has completed business verification"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Merchant Profile")
        verbose_name_plural = _("Merchant Profiles")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.company_name} ({self.user.username})"

    @property
    def has_location(self) -> bool:
        """Check if merchant has geographic coordinates set."""
        return self.latitude is not None and self.longitude is not None


class Subscription(models.Model):
    """Merchant subscription tier management."""

    TIER_CHOICES = [
        ("free", _("Free Tier (7.3% commission)")),
        ("premium", _("Premium Tier (3.1% commission)")),
    ]

    STATUS_CHOICES = [
        ("active", _("Active")),
        ("cancelled", _("Cancelled")),
        ("suspended", _("Suspended")),
        ("expired", _("Expired")),
    ]

    merchant = models.OneToOneField(
        MerchantProfile,
        on_delete=models.CASCADE,
        related_name="subscription",
        verbose_name=_("Merchant"),
    )
    tier = models.CharField(
        max_length=20,
        choices=TIER_CHOICES,
        default="free",
        verbose_name=_("Subscription Tier"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        verbose_name=_("Status"),
    )

    # Premium subscription dates
    premium_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Premium Started At"),
    )
    premium_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Premium Expires At"),
    )

    # Billing
    last_payment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Payment Date"),
    )
    next_billing_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Next Billing Date"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.merchant.company_name} - {self.get_tier_display()}"

    @property
    def commission_rate(self) -> Decimal:
        """Get commission rate based on tier."""
        if self.tier == "premium":
            return Decimal("3.1")
        return Decimal("7.3")

    @property
    def monthly_fee(self) -> Decimal:
        """Get monthly fee based on tier."""
        if self.tier == "premium":
            return Decimal("299.00")
        return Decimal("0.00")

    @property
    def is_premium(self) -> bool:
        """Check if subscription is premium tier."""
        return self.tier == "premium" and self.status == "active"


class Shop(models.Model):
    """Merchant's online shop configuration."""

    merchant = models.ForeignKey(
        MerchantProfile,
        on_delete=models.CASCADE,
        related_name="shops",
        verbose_name=_("Merchant"),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Shop Name"),
        help_text=_("Display name for customers"),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name=_("URL Slug"),
        help_text=_("Used in shop URL"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Tell customers about your shop"),
    )

    # Shop logo and branding
    logo = models.ImageField(
        upload_to="shops/logos/",
        null=True,
        blank=True,
        verbose_name=_("Logo"),
    )
    banner = models.ImageField(
        upload_to="shops/banners/",
        null=True,
        blank=True,
        verbose_name=_("Banner Image"),
    )

    # Contact information
    email = models.EmailField(verbose_name=_("Contact Email"))
    phone = models.CharField(max_length=20, verbose_name=_("Contact Phone"))

    # Operating radius for local delivery
    delivery_radius_km = models.PositiveIntegerField(
        default=150,
        validators=[MaxValueValidator(500)],
        verbose_name=_("Delivery Radius (km)"),
        help_text=_("Maximum distance for deliveries"),
    )

    # Shop settings
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Shop is visible to customers"),
    )
    accepts_online_orders = models.BooleanField(
        default=True,
        verbose_name=_("Accepts Online Orders"),
    )
    accepts_in_store_pickup = models.BooleanField(
        default=True,
        verbose_name=_("Accepts In-Store Pickup"),
    )

    # Statistics (updated by signals/tasks)
    total_products = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Products"),
    )
    total_orders = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Orders"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Shop")
        verbose_name_plural = _("Shops")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["merchant", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def is_operational(self) -> bool:
        """Check if shop is ready to accept orders."""
        return (
                self.is_active
                and self.merchant.is_verified
                and self.merchant.subscription.status == "active"
        )