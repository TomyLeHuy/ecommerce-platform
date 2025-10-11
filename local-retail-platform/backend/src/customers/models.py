"""Customer models for the Local Retail Platform."""

from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from src.merchants.models import Shop


class CustomerProfile(models.Model):
    """Extended profile for customer users."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile",
        verbose_name=_("User"),
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Phone Number"),
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date of Birth"),
    )

    # Shipping Address
    street_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Street Address"),
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("City"),
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("Postal Code"),
    )
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
        help_text=_("Current location for local search"),
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        verbose_name=_("Longitude"),
        help_text=_("Current location for local search"),
    )

    # Search preferences
    default_search_radius_km = models.PositiveIntegerField(
        default=150,
        validators=[MaxValueValidator(500)],
        verbose_name=_("Default Search Radius (km)"),
        help_text=_("Preferred radius for local shop search"),
    )

    # Preferences
    newsletter_subscribed = models.BooleanField(
        default=False,
        verbose_name=_("Newsletter Subscription"),
    )
    marketing_consent = models.BooleanField(
        default=False,
        verbose_name=_("Marketing Consent"),
    )

    # Statistics
    total_orders = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Orders"),
    )
    total_spent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Total Spent (€)"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Customer Profile")
        verbose_name_plural = _("Customer Profiles")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user.get_full_name() or self.user.username}"

    @property
    def has_location(self) -> bool:
        """Check if customer has location set."""
        return self.latitude is not None and self.longitude is not None

    @property
    def has_complete_profile(self) -> bool:
        """Check if customer has filled all essential info."""
        return bool(
            self.street_address
            and self.city
            and self.postal_code
            and self.phone
        )


class FavoriteShop(models.Model):
    """Customer's saved favorite shops (for travel feature)."""

    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="favorite_shops",
        verbose_name=_("Customer"),
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name=_("Shop"),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
        help_text=_("Personal notes about this shop"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Favorite Shop")
        verbose_name_plural = _("Favorite Shops")
        ordering = ["-created_at"]
        unique_together = [["customer", "shop"]]
        indexes = [
            models.Index(fields=["customer", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.customer.user.username} → {self.shop.name}"


class LoyaltyToken(models.Model):
    """Customer loyalty token balance and transaction history."""

    TRANSACTION_TYPE_CHOICES = [
        ("earned", _("Earned from Purchase")),
        ("spent", _("Spent on Order")),
        ("expired", _("Expired")),
        ("admin_adjustment", _("Admin Adjustment")),
    ]

    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="token_transactions",
        verbose_name=_("Customer"),
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name=_("Transaction Type"),
    )
    amount = models.IntegerField(
        verbose_name=_("Token Amount"),
        help_text=_("Positive for earned, negative for spent"),
    )
    balance_after = models.IntegerField(
        default=0,
        verbose_name=_("Balance After Transaction"),
    )

    # Reference to related order (if applicable)
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="token_transactions",
        verbose_name=_("Related Order"),
    )

    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Description"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Loyalty Token Transaction")
        verbose_name_plural = _("Loyalty Token Transactions")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["customer", "-created_at"]),
        ]

    def __str__(self) -> str:
        sign = "+" if self.amount > 0 else ""
        return f"{self.customer.user.username}: {sign}{self.amount} tokens"

    @classmethod
    def get_customer_balance(cls, customer: CustomerProfile) -> int:
        """Get current token balance for a customer."""
        last_transaction = cls.objects.filter(customer=customer).first()
        return last_transaction.balance_after if last_transaction else 0

    @property
    def token_value_euros(self) -> Decimal:
        """Get euro value of this transaction."""
        from src.config.configManager import config_manager
        token_value = Decimal(str(config_manager.config.business.loyalty.token_value_euro))
        return abs(self.amount) * token_value


class DigitalReceipt(models.Model):
    """Digital receipt inbox for customers (Kassenzettel management)."""

    RECEIPT_TYPE_CHOICES = [
        ("online", _("Online Order")),
        ("in_store", _("In-Store Purchase")),
    ]

    EXPENSE_TYPE_CHOICES = [
        ("personal", _("Personal")),
        ("business", _("Business")),
    ]

    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="receipts",
        verbose_name=_("Customer"),
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.SET_NULL,
        null=True,
        related_name="receipts_issued",
        verbose_name=_("Shop"),
    )
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="receipt",
        verbose_name=_("Related Order"),
    )

    # Receipt Details
    receipt_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Receipt Number"),
    )
    receipt_type = models.CharField(
        max_length=20,
        choices=RECEIPT_TYPE_CHOICES,
        default="online",
        verbose_name=_("Receipt Type"),
    )
    expense_type = models.CharField(
        max_length=20,
        choices=EXPENSE_TYPE_CHOICES,
        default="personal",
        verbose_name=_("Expense Type"),
        help_text=_("For tax categorization"),
    )

    # Purchase Information
    purchase_date = models.DateTimeField(
        verbose_name=_("Purchase Date"),
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Total Amount (€)"),
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Tax Amount (€)"),
    )

    # Return Policy
    return_deadline = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Return Deadline"),
        help_text=_("Last date for returns"),
    )
    is_returnable = models.BooleanField(
        default=True,
        verbose_name=_("Returnable"),
    )

    # Document Storage
    pdf_file = models.FileField(
        upload_to="receipts/%Y/%m/",
        null=True,
        blank=True,
        verbose_name=_("PDF Receipt"),
    )

    # Status
    is_archived = models.BooleanField(
        default=False,
        verbose_name=_("Archived"),
        help_text=_("Archive after return deadline expires"),
    )

    # DATEV Export
    exported_to_datev = models.BooleanField(
        default=False,
        verbose_name=_("Exported to DATEV"),
    )
    datev_export_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("DATEV Export Date"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Digital Receipt")
        verbose_name_plural = _("Digital Receipts")
        ordering = ["-purchase_date"]
        indexes = [
            models.Index(fields=["customer", "-purchase_date"]),
            models.Index(fields=["receipt_number"]),
            models.Index(fields=["expense_type", "is_archived"]),
        ]

    def __str__(self) -> str:
        return f"Receipt {self.receipt_number} - {self.shop.name if self.shop else 'Unknown'}"

    @property
    def is_return_period_active(self) -> bool:
        """Check if receipt is still within return period."""
        if not self.return_deadline or not self.is_returnable:
            return False
        from django.utils import timezone
        return timezone.now().date() <= self.return_deadline

    @property
    def days_until_return_deadline(self) -> int | None:
        """Calculate days remaining for returns."""
        if not self.return_deadline:
            return None
        from django.utils import timezone
        delta = self.return_deadline - timezone.now().date()
        return max(0, delta.days)