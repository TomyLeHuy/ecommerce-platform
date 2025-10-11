"""Order models for the Local Retail Platform."""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from src.customers.models import CustomerProfile
from src.merchants.models import Shop
from src.products.models import Product


class Order(models.Model):
    """Customer order management."""

    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("confirmed", _("Confirmed")),
        ("processing", _("Processing")),
        ("shipped", _("Shipped")),
        ("delivered", _("Delivered")),
        ("cancelled", _("Cancelled")),
        ("refunded", _("Refunded")),
    ]

    FULFILLMENT_METHOD_CHOICES = [
        ("delivery", _("Home Delivery")),
        ("pickup", _("In-Store Pickup")),
    ]

    # Core relationships
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name=_("Customer"),
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name=_("Shop"),
    )

    # Order identification
    order_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Order Number"),
        help_text=_("Unique order identifier"),
    )

    # Order status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
    )
    fulfillment_method = models.CharField(
        max_length=20,
        choices=FULFILLMENT_METHOD_CHOICES,
        default="delivery",
        verbose_name=_("Fulfillment Method"),
    )

    # Shipping address (copied from customer profile at order time)
    shipping_street_address = models.CharField(
        max_length=255,
        verbose_name=_("Shipping Street"),
    )
    shipping_city = models.CharField(
        max_length=100,
        verbose_name=_("Shipping City"),
    )
    shipping_postal_code = models.CharField(
        max_length=10,
        verbose_name=_("Shipping Postal Code"),
    )
    shipping_country = models.CharField(
        max_length=2,
        default="DE",
        verbose_name=_("Shipping Country"),
    )

    # Pricing
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Subtotal (€)"),
        help_text=_("Sum of all items before tax and shipping"),
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Tax Amount (€)"),
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Shipping Cost (€)"),
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Discount Amount (€)"),
    )
    tokens_used = models.IntegerField(
        default=0,
        verbose_name=_("Loyalty Tokens Used"),
    )
    tokens_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Token Discount Value (€)"),
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Total Amount (€)"),
    )

    # Payment info
    payment_status = models.CharField(
        max_length=20,
        default="pending",
        verbose_name=_("Payment Status"),
    )
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Payment Method"),
    )

    # Customer notes
    customer_notes = models.TextField(
        blank=True,
        verbose_name=_("Customer Notes"),
        help_text=_("Special delivery instructions"),
    )

    # Tracking
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Tracking Number"),
    )
    tracking_url = models.URLField(
        blank=True,
        verbose_name=_("Tracking URL"),
    )

    # Timestamps
    ordered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Ordered At"),
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Confirmed At"),
    )
    shipped_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Shipped At"),
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Delivered At"),
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Cancelled At"),
    )

    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ["-ordered_at"]
        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["customer", "-ordered_at"]),
            models.Index(fields=["shop", "-ordered_at"]),
            models.Index(fields=["status", "-ordered_at"]),
        ]

    def __str__(self) -> str:
        return f"Order {self.order_number} - {self.customer.user.username}"

    def save(self, *args, **kwargs):
        """Generate order number if not provided."""
        if not self.order_number:
            from django.utils.crypto import get_random_string
            import time
            timestamp = int(time.time())
            random_str = get_random_string(6, "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            self.order_number = f"ORD-{timestamp}-{random_str}"
        super().save(*args, **kwargs)

    @property
    def is_paid(self) -> bool:
        """Check if order is paid."""
        return self.payment_status == "completed"

    @property
    def can_be_cancelled(self) -> bool:
        """Check if order can be cancelled."""
        return self.status in ["pending", "confirmed"]

    @property
    def is_completed(self) -> bool:
        """Check if order is completed."""
        return self.status in ["delivered", "cancelled", "refunded"]


class OrderItem(models.Model):
    """Individual items in an order."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Order"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name=_("Product"),
        help_text=_("PROTECT: Keep product history even if deleted"),
    )

    # Product snapshot (prices at time of order)
    product_name = models.CharField(
        max_length=255,
        verbose_name=_("Product Name"),
        help_text=_("Snapshot at order time"),
    )
    product_sku = models.CharField(
        max_length=100,
        verbose_name=_("Product SKU"),
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name=_("Unit Price (€)"),
        help_text=_("Price per item at order time"),
    )

    # Quantity and totals
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_("Quantity"),
    )
    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Line Total (€)"),
        help_text=_("unit_price × quantity"),
    )

    # Tax calculation
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("19.00"),
        verbose_name=_("Tax Rate (%)"),
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Tax Amount (€)"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["order", "product"]),
        ]

    def __str__(self) -> str:
        return f"{self.quantity}× {self.product_name}"

    def save(self, *args, **kwargs):
        """Calculate line total and tax."""
        # Calculate line total
        self.line_total = self.unit_price * self.quantity

        # Calculate tax amount
        tax_multiplier = self.tax_rate / Decimal("100")
        self.tax_amount = (self.line_total * tax_multiplier) / (Decimal("1") + tax_multiplier)

        # Copy product info if not set
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_sku:
            self.product_sku = self.product.sku

        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """Track order status changes for audit trail."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name=_("Order"),
    )
    status = models.CharField(
        max_length=20,
        verbose_name=_("Status"),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
    )
    changed_by = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Changed By"),
        help_text=_("User who made the change"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Changed At"))

    class Meta:
        verbose_name = _("Order Status History")
        verbose_name_plural = _("Order Status Histories")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.order.order_number} → {self.status}"