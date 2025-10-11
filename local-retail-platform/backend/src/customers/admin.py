"""Django admin configuration for Customers app."""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import CustomerProfile, DigitalReceipt, FavoriteShop, LoyaltyToken


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    """Admin interface for CustomerProfile."""

    list_display = [
        "user",
        "full_name_display",
        "city",
        "has_location_display",
        "token_balance_display",
        "total_orders",
        "total_spent_display",
        "created_at",
    ]
    list_filter = [
        "newsletter_subscribed",
        "marketing_consent",
        "country",
        "created_at",
    ]
    search_fields = [
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "phone",
        "city",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
        "total_orders",
        "total_spent",
        "token_balance_display",
    ]

    fieldsets = (
        (
            _("User Information"),
            {
                "fields": ("user", "phone", "date_of_birth"),
            },
        ),
        (
            _("Address"),
            {
                "fields": (
                    "street_address",
                    "city",
                    "postal_code",
                    "country",
                ),
            },
        ),
        (
            _("Location Settings"),
            {
                "fields": (
                    "latitude",
                    "longitude",
                    "default_search_radius_km",
                ),
            },
        ),
        (
            _("Preferences"),
            {
                "fields": (
                    "newsletter_subscribed",
                    "marketing_consent",
                ),
            },
        ),
        (
            _("Statistics"),
            {
                "fields": (
                    "token_balance_display",
                    "total_orders",
                    "total_spent",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def full_name_display(self, obj):
        """Display customer full name."""
        return obj.user.get_full_name() or "—"

    full_name_display.short_description = _("Full Name")

    def has_location_display(self, obj):
        """Display location status."""
        if obj.has_location:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')

    has_location_display.short_description = _("Location")

    def token_balance_display(self, obj):
        """Display current token balance."""
        balance = LoyaltyToken.get_customer_balance(obj)
        return format_html(
            '<span style="font-weight: bold; color: #0066cc;">{} tokens</span>',
            balance,
        )

    token_balance_display.short_description = _("Token Balance")

    def total_spent_display(self, obj):
        """Display total spent with currency."""
        return f"€{obj.total_spent}"

    total_spent_display.short_description = _("Total Spent")


@admin.register(FavoriteShop)
class FavoriteShopAdmin(admin.ModelAdmin):
    """Admin interface for FavoriteShop."""

    list_display = [
        "customer",
        "shop",
        "shop_location",
        "created_at",
    ]
    list_filter = ["created_at"]
    search_fields = [
        "customer__user__username",
        "customer__user__email",
        "shop__name",
        "shop__merchant__company_name",
    ]
    readonly_fields = ["created_at"]

    fieldsets = (
        (
            _("Favorite Details"),
            {
                "fields": ("customer", "shop", "notes"),
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

    def shop_location(self, obj):
        """Display shop city."""
        return obj.shop.merchant.city

    shop_location.short_description = _("Shop Location")


@admin.register(LoyaltyToken)
class LoyaltyTokenAdmin(admin.ModelAdmin):
    """Admin interface for LoyaltyToken."""

    list_display = [
        "customer",
        "transaction_type",
        "amount_display",
        "balance_after",
        "token_value_display",
        "order",
        "created_at",
    ]
    list_filter = ["transaction_type", "created_at"]
    search_fields = [
        "customer__user__username",
        "customer__user__email",
        "description",
    ]
    readonly_fields = ["created_at", "token_value_display"]

    fieldsets = (
        (
            _("Transaction Details"),
            {
                "fields": (
                    "customer",
                    "transaction_type",
                    "amount",
                    "balance_after",
                    "token_value_display",
                ),
            },
        ),
        (
            _("References"),
            {
                "fields": ("order", "description"),
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

    def amount_display(self, obj):
        """Display amount with color coding."""
        color = "green" if obj.amount > 0 else "red"
        sign = "+" if obj.amount > 0 else ""
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}{}</span>',
            color,
            sign,
            obj.amount,
        )

    amount_display.short_description = _("Amount")

    def token_value_display(self, obj):
        """Display euro value of tokens."""
        return f"€{obj.token_value_euros}"

    token_value_display.short_description = _("Euro Value")


@admin.register(DigitalReceipt)
class DigitalReceiptAdmin(admin.ModelAdmin):
    """Admin interface for DigitalReceipt."""

    list_display = [
        "receipt_number",
        "customer",
        "shop",
        "purchase_date",
        "total_amount_display",
        "expense_type",
        "return_status_display",
        "is_archived",
    ]
    list_filter = [
        "receipt_type",
        "expense_type",
        "is_archived",
        "is_returnable",
        "exported_to_datev",
        "purchase_date",
    ]
    search_fields = [
        "receipt_number",
        "customer__user__username",
        "customer__user__email",
        "shop__name",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
        "return_status_display",
        "days_remaining_display",
    ]
    date_hierarchy = "purchase_date"

    fieldsets = (
        (
            _("Receipt Information"),
            {
                "fields": (
                    "receipt_number",
                    "customer",
                    "shop",
                    "order",
                    "receipt_type",
                ),
            },
        ),
        (
            _("Financial Details"),
            {
                "fields": (
                    "purchase_date",
                    "total_amount",
                    "tax_amount",
                    "expense_type",
                ),
            },
        ),
        (
            _("Return Policy"),
            {
                "fields": (
                    "is_returnable",
                    "return_deadline",
                    "return_status_display",
                    "days_remaining_display",
                ),
            },
        ),
        (
            _("Document"),
            {
                "fields": ("pdf_file",),
                "classes": ("collapse",),
            },
        ),
        (
            _("DATEV Integration"),
            {
                "fields": (
                    "exported_to_datev",
                    "datev_export_date",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("is_archived", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def total_amount_display(self, obj):
        """Display total amount with currency."""
        return f"€{obj.total_amount}"

    total_amount_display.short_description = _("Total")

    def return_status_display(self, obj):
        """Display return status with visual indicator."""
        if not obj.is_returnable:
            return format_html(
                '<span style="color: gray;">Not Returnable</span>'
            )

        if obj.is_return_period_active:
            days = obj.days_until_return_deadline
            color = "green" if days and days > 7 else "orange"
            return format_html(
                '<span style="color: {};">✓ Active ({} days left)</span>',
                color,
                days or 0,
            )

        return format_html(
            '<span style="color: red;">✗ Expired</span>'
        )

    return_status_display.short_description = _("Return Status")

    def days_remaining_display(self, obj):
        """Display days until return deadline."""
        days = obj.days_until_return_deadline
        if days is None:
            return "—"
        return f"{days} days"

    days_remaining_display.short_description = _("Days Remaining")

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related("customer__user", "shop", "order")