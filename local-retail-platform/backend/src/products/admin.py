"""Django admin configuration for Products app."""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category."""

    list_display = [
        "name",
        "parent",
        "is_active",
        "display_order",
        "product_count",
    ]
    list_filter = ["is_active", "parent"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            _("Category Information"),
            {
                "fields": ("name", "slug", "description", "parent"),
            },
        ),
        (
            _("Display Settings"),
            {
                "fields": ("icon", "is_active", "display_order"),
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

    def product_count(self, obj):
        """Display number of products in category."""
        count = obj.products.count()
        return f"{count} products"

    product_count.short_description = _("Products")


class ProductImageInline(admin.TabularInline):
    """Inline admin for product images."""

    model = ProductImage
    extra = 1
    fields = ["image", "alt_text", "display_order", "is_primary"]
    readonly_fields = ["created_at"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product."""

    list_display = [
        "name",
        "shop",
        "category",
        "price_display",
        "stock_status_display",
        "stock_quantity",
        "is_active",
        "sales_count",
    ]
    list_filter = [
        "is_active",
        "is_featured",
        "category",
        "shop",
        "created_at",
    ]
    search_fields = [
        "name",
        "sku",
        "barcode",
        "description",
        "shop__name",
    ]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = [
        "created_at",
        "updated_at",
        "view_count",
        "sales_count",
        "profit_margin_display",
        "stock_status_display",
    ]
    inlines = [ProductImageInline]

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": (
                    "shop",
                    "category",
                    "name",
                    "slug",
                    "short_description",
                    "description",
                ),
            },
        ),
        (
            _("Product Identification"),
            {
                "fields": ("sku", "barcode"),
            },
        ),
        (
            _("Pricing"),
            {
                "fields": (
                    "price",
                    "sale_price",
                    "cost_price",
                    "profit_margin_display",
                ),
            },
        ),
        (
            _("Inventory Management"),
            {
                "fields": (
                    "stock_quantity",
                    "min_stock_level",
                    "max_stock_level",
                    "stock_status_display",
                ),
            },
        ),
        (
            _("Product Attributes"),
            {
                "fields": (
                    "weight_kg",
                    "length_cm",
                    "width_cm",
                    "height_cm",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Status & Visibility"),
            {
                "fields": ("is_active", "is_featured"),
            },
        ),
        (
            _("SEO"),
            {
                "fields": ("meta_title", "meta_description"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Statistics"),
            {
                "fields": ("view_count", "sales_count", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def price_display(self, obj):
        """Display price with sale price if applicable."""
        if obj.sale_price and obj.sale_price < obj.price:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">€{}</span> '
                '<span style="color: red; font-weight: bold;">€{}</span>',
                obj.price,
                obj.sale_price,
            )
        return f"€{obj.price}"

    price_display.short_description = _("Price")

    def stock_status_display(self, obj):
        """Display visual stock status indicator."""
        status = obj.stock_status
        if status == "out_of_stock":
            color = "red"
            icon = "✗"
            text = "Out of Stock"
        elif status == "low_stock":
            color = "orange"
            icon = "⚠"
            text = f"Low Stock ({obj.stock_quantity})"
        else:
            color = "green"
            icon = "✓"
            text = f"In Stock ({obj.stock_quantity})"

        return format_html(
            '<span style="color: {};">{} {}</span>',
            color,
            icon,
            text,
        )

    stock_status_display.short_description = _("Stock Status")

    def profit_margin_display(self, obj):
        """Display profit margin percentage."""
        margin = obj.profit_margin
        if margin is not None:
            color = "green" if margin > 30 else "orange" if margin > 10 else "red"
            return format_html(
                '<span style="color: {};">{:.2f}%</span>',
                color,
                margin,
            )
        return "—"

    profit_margin_display.short_description = _("Profit Margin")

    def get_queryset(self, request):
        """Optimize queryset with related objects."""
        qs = super().get_queryset(request)
        return qs.select_related("shop", "category", "shop__merchant")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin interface for ProductImage."""

    list_display = [
        "product",
        "image_preview",
        "is_primary",
        "display_order",
        "created_at",
    ]
    list_filter = ["is_primary", "created_at"]
    search_fields = ["product__name", "alt_text"]
    readonly_fields = ["created_at", "image_preview"]

    fieldsets = (
        (
            _("Image Information"),
            {
                "fields": ("product", "image", "image_preview", "alt_text"),
            },
        ),
        (
            _("Display Settings"),
            {
                "fields": ("display_order", "is_primary"),
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

    def image_preview(self, obj):
        """Display image preview in admin."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;" />',
                obj.image.url,
            )
        return "—"

    image_preview.short_description = _("Preview")