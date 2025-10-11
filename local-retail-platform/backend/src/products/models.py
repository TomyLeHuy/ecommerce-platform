"""Product models for the Local Retail Platform."""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from src.merchants.models import Shop


class Category(models.Model):
    """Product category hierarchy."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Category Name"),
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_("URL Slug"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
        verbose_name=_("Parent Category"),
        help_text=_("Leave empty for top-level category"),
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Icon Class"),
        help_text=_("CSS icon class name"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["display_order", "name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["parent", "is_active"]),
        ]

    def __str__(self) -> str:
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def full_path(self) -> str:
        """Get full category path."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class Product(models.Model):
    """Product listing by merchants."""

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Shop"),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products",
        verbose_name=_("Category"),
    )

    # Basic Information
    name = models.CharField(
        max_length=255,
        verbose_name=_("Product Name"),
    )
    slug = models.SlugField(
        max_length=255,
        verbose_name=_("URL Slug"),
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Detailed product description"),
    )
    short_description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Short Description"),
        help_text=_("Brief product summary"),
    )

    # SKU (Stock Keeping Unit)
    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("SKU"),
        help_text=_("Unique product identifier"),
    )
    barcode = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Barcode/EAN"),
    )

    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name=_("Price (€)"),
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name=_("Sale Price (€)"),
        help_text=_("Optional discounted price"),
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name=_("Cost Price (€)"),
        help_text=_("Your cost for inventory management"),
    )

    # Inventory Management
    stock_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Stock Quantity"),
    )
    min_stock_level = models.IntegerField(
        default=5,
        validators=[MinValueValidator(0)],
        verbose_name=_("Minimum Stock Level"),
        help_text=_("Trigger restock notification at this level"),
    )
    max_stock_level = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name=_("Maximum Stock Level"),
        help_text=_("Target stock level for reordering"),
    )

    # Product Attributes
    weight_kg = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.001"))],
        verbose_name=_("Weight (kg)"),
    )
    length_cm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Length (cm)"),
    )
    width_cm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Width (cm)"),
    )
    height_cm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Height (cm)"),
    )

    # Product Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Product is visible and available for purchase"),
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured"),
        help_text=_("Show in featured products"),
    )

    # SEO
    meta_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name=_("Meta Title"),
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name=_("Meta Description"),
    )

    # Statistics (updated via signals/tasks)
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("View Count"),
    )
    sales_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Sales"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["shop", "is_active"]),
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["sku"]),
        ]
        unique_together = [["shop", "slug"]]

    def __str__(self) -> str:
        return f"{self.name} ({self.shop.name})"

    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided."""
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            # Ensure unique slug per shop
            counter = 1
            while Product.objects.filter(shop=self.shop, slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    @property
    def current_price(self) -> Decimal:
        """Get the active selling price (sale price if available)."""
        if self.sale_price and self.sale_price < self.price:
            return self.sale_price
        return self.price

    @property
    def is_in_stock(self) -> bool:
        """Check if product is in stock."""
        return self.stock_quantity > 0

    @property
    def is_low_stock(self) -> bool:
        """Check if product stock is below minimum level."""
        return 0 < self.stock_quantity <= self.min_stock_level

    @property
    def stock_status(self) -> str:
        """Get human-readable stock status."""
        if self.stock_quantity == 0:
            return "out_of_stock"
        elif self.is_low_stock:
            return "low_stock"
        return "in_stock"

    @property
    def profit_margin(self) -> Decimal | None:
        """Calculate profit margin if cost price is set."""
        if self.cost_price:
            profit = self.current_price - self.cost_price
            if self.cost_price > 0:
                return (profit / self.cost_price) * 100
        return None


class ProductImage(models.Model):
    """Product images for gallery display."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Product"),
    )
    image = models.ImageField(
        upload_to="products/%Y/%m/",
        verbose_name=_("Image"),
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Alt Text"),
        help_text=_("Image description for accessibility"),
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("Primary Image"),
        help_text=_("Main product image"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        ordering = ["display_order", "created_at"]
        indexes = [
            models.Index(fields=["product", "is_primary"]),
        ]

    def __str__(self) -> str:
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        """Ensure only one primary image per product."""
        if self.is_primary:
            # Set all other images for this product as non-primary
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)