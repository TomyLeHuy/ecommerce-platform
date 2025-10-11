"""Django admin configuration for Orders app."""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""

    model = OrderItem
    extra = 0
    fields = [
        "product",
        "product_name",
        "product_sku",
        "unit_price",
        "quantity",
        "line_total",
        "tax_rate",
        "tax_amount",
    ]
    readonly_fields = ["line_total", "tax_amount", "product_name", "product_sku"]


class OrderStatusHistoryInline(admin.TabularInline):
    """Inline admin for order status history."""

    model = OrderStatusHistory
    extra = 0
    fields = ["status", "notes", "changed_by", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order."""

    list_display = [
        "order_number",
        "customer",
        "shop",
        "status_display",
        "payment_status_display",
        "total_display",
        "fulfillment_method",
        "ordered_at",
    ]
    list_filter = [
        "status",
        "payment_status",
        "fulfillment_method",
        "ordered_at",
        "shop",
    ]
    search_fields = [
        "order_number",
        "customer__user__username",
        "customer__user__email",
        "shop__name",
        "tracking_number",
    ]
    readonly_fields = [
        "order_number",
        "ordered_at",
        "updated_at",
        "confirmed_at",
        "shipped_at",
        "delivered_at",
        "cancelled_at",
        "subtotal",
        "tax_amount",
        "total",
    ]
    date_hierarchy = "ordered_at"
    inlines = [OrderItemInline, OrderStatusHistoryInline]

    fieldsets = (
        (
            _("Order Information"),
            {
                "fields": (
                    "order_number",
                    "customer",
                    "shop",
                    "status",
                    "fulfillment_method",
                ),
            },
        ),
        (
            _("Shipping Address"),
            {
                "fields": (
                    "shipping_street_address",
                    "shipping_city",
                    "shipping_postal_code",
                    "shipping_country",
                ),
            },
        ),
        (
            _("Pricing"),
            {
                "fields": (
                    "subtotal",
                    "tax_amount",
                    "shipping_cost",
                    "discount_amount",
                    "tokens_used",
                    "tokens_value",
                    "total",
                ),
            },
        ),
        (
            _("Payment"),
            {
                "fields": ("payment_status", "payment_method"),
            },
        ),
        (
            _("Shipping & Tracking"),
            {
                "fields": (
                    "tracking_number",
                    "tracking_url",
                    "customer_notes",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "ordered_at",
                    "confirmed_at",
                    "shipped_at",
                    "delivered_at",
                    "cancelled_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def status_display(self, obj):
        """Display order status with color."""
        status_colors = {
            "pending": "#FFA500",  # Orange
            "confirmed": "#4169E1",  # Royal Blue
            "processing": "#9370DB",  # Medium Purple
            "shipped": "#20B2AA",  # Light Sea Green
            "delivered": "#228B22",  # Forest Green
            "cancelled": "#DC143C",  # Crimson
            "refunded": "#8B4513",  # Saddle Brown
        }
        color = status_colors.get(obj.status, "#000000")
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = _("Status")

    def payment_status_display(self, obj):
        """Display payment status with icon."""
        if obj.is_paid:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Paid</span>'
            )
        return format_html(
            '<span style="color: orange;">⏳ {}</span>',
            obj.payment_status.title(),
        )

    payment_status_display.short_description = _("Payment")

    def total_display(self, obj):
        """Display total amount."""
        return f"€{obj.total}"

    total_display.short_description = _("Total")

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related(
            "customer__user",
            "shop",
            "shop__merchant",
        ).prefetch_related("items")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for OrderItem."""

    list_display = [
        "order",
        "product_name",
        "product_sku",
        "quantity",
        "unit_price_display",
        "line_total_display",
        "created_at",
    ]
    list_filter = ["created_at"]
    search_fields = [
        "order__order_number",
        "product_name",
        "product_sku",
        "product__name",
    ]
    readonly_fields = ["line_total", "tax_amount", "created_at"]

    fieldsets = (
        (
            _("Order & Product"),
            {
                "fields": ("order", "product"),
            },
        ),
        (
            _("Product Snapshot"),
            {
                "fields": ("product_name", "product_sku", "unit_price"),
            },
        ),
        (
            _("Quantity & Pricing"),
            {
                "fields": ("quantity", "line_total", "tax_rate", "tax_amount"),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )

    def unit_price_display(self, obj):
        """Display unit price."""
        return f"€{obj.unit_price}"

    unit_price_display.short_description = _("Unit Price")

    def line_total_display(self, obj):
        """Display line total."""
        return f"€{obj.line_total}"

    line_total_display.short_description = _("Total")


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """Admin interface for OrderStatusHistory."""

    list_display = [
        "order",
        "status",
        "changed_by",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = [
        "order__order_number",
        "notes",
        "changed_by",
    ]
    readonly_fields = ["created_at"]

    fieldsets = (
        (
            _("Status Change"),
            {
                "fields": ("order", "status", "changed_by", "notes"),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("created_at",),
            },
        ),
    )