"""Django admin configuration for Merchants app."""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import MerchantProfile, Shop, Subscription


@admin.register(MerchantProfile)
class MerchantProfileAdmin(admin.ModelAdmin):
    """Admin interface for MerchantProfile."""

    list_display = [
        "company_name",
        "user",
        "city",
        "is_verified",
        "has_location_display",
        "created_at",
    ]
    list_filter = ["is_verified", "country", "created_at"]
    search_fields = ["company_name", "user__username", "user__email", "tax_id", "city"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            _("User Information"),
            {
                "fields": ("user", "company_name", "tax_id", "phone"),
            },
        ),
        (
            _("Business Address"),
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
            _("Geographic Location"),
            {
                "fields": ("latitude", "longitude"),
                "description": _("Coordinates for location-based search"),
            },
        ),
        (
            _("Integrations"),
            {
                "fields": ("datev_client_id",),
                "classes": ("collapse",),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("is_verified", "created_at", "updated_at"),
            },
        ),
    )

    def has_location_display(self, obj):
        """Display if merchant has coordinates set."""
        if obj.has_location:
            return format_html(
                '<span style="color: green;">✓</span>'
            )
        return format_html(
            '<span style="color: red;">✗</span>'
        )

    has_location_display.short_description = _("Location Set")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for Subscription."""

    list_display = [
        "merchant",
        "tier",
        "status",
        "commission_display",
        "monthly_fee_display",
        "next_billing_date",
    ]
    list_filter = ["tier", "status", "created_at"]
    search_fields = ["merchant__company_name", "merchant__user__username"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            _("Subscription Details"),
            {
                "fields": ("merchant", "tier", "status"),
            },
        ),
        (
            _("Premium Subscription"),
            {
                "fields": (
                    "premium_started_at",
                    "premium_expires_at",
                ),
            },
        ),
        (
            _("Billing Information"),
            {
                "fields": (
                    "last_payment_date",
                    "next_billing_date",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def commission_display(self, obj):
        """Display commission rate."""
        return f"{obj.commission_rate}%"

    commission_display.short_description = _("Commission")

    def monthly_fee_display(self, obj):
        """Display monthly fee."""
        return f"€{obj.monthly_fee}"

    monthly_fee_display.short_description = _("Monthly Fee")


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    """Admin interface for Shop."""

    list_display = [
        "name",
        "merchant",
        "is_active",
        "is_operational_display",
        "total_products",
        "total_orders",
        "created_at",
    ]
    list_filter = [
        "is_active",
        "accepts_online_orders",
        "accepts_in_store_pickup",
        "created_at",
    ]
    search_fields = [
        "name",
        "slug",
        "merchant__company_name",
        "email",
    ]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at", "total_products", "total_orders"]

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": ("merchant", "name", "slug", "description"),
            },
        ),
        (
            _("Branding"),
            {
                "fields": ("logo", "banner"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Contact Information"),
            {
                "fields": ("email", "phone"),
            },
        ),
        (
            _("Shop Settings"),
            {
                "fields": (
                    "delivery_radius_km",
                    "is_active",
                    "accepts_online_orders",
                    "accepts_in_store_pickup",
                ),
            },
        ),
        (
            _("Statistics"),
            {
                "fields": ("total_products", "total_orders"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def is_operational_display(self, obj):
        """Display operational status."""
        if obj.is_operational:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Operational</span>'
            )
        return format_html(
            '<span style="color: orange;">⚠ Not Operational</span>'
        )

    is_operational_display.short_description = _("Status")