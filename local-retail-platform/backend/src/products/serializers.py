"""API serializers for Products app."""

from rest_framework import serializers

from src.merchants.models import Shop
from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""

    full_path = serializers.ReadOnlyField()
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "parent",
            "full_path",
            "icon",
            "is_active",
            "display_order",
            "subcategories",
        ]
        read_only_fields = ["id", "full_path"]

    def get_subcategories(self, obj):
        """Get child categories."""
        if obj.subcategories.exists():
            return CategorySerializer(
                obj.subcategories.filter(is_active=True),
                many=True,
                context=self.context
            ).data
        return []


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model."""

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "alt_text",
            "display_order",
            "is_primary",
        ]
        read_only_fields = ["id"]


class ShopBasicSerializer(serializers.ModelSerializer):
    """Basic shop info for product listings."""

    merchant_name = serializers.CharField(source="merchant.company_name", read_only=True)
    merchant_city = serializers.CharField(source="merchant.city", read_only=True)

    class Meta:
        model = Shop
        fields = [
            "id",
            "name",
            "slug",
            "logo",
            "merchant_name",
            "merchant_city",
            "is_active",
        ]
        read_only_fields = ["id"]


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list view (minimal data)."""

    current_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    stock_status = serializers.CharField(read_only=True)
    primary_image = serializers.SerializerMethodField()
    shop = ShopBasicSerializer(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "sku",
            "price",
            "sale_price",
            "current_price",
            "stock_status",
            "is_in_stock",
            "primary_image",
            "shop",
            "category_name",
            "is_featured",
        ]
        read_only_fields = ["id"]

    def get_primary_image(self, obj):
        """Get primary product image."""
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(primary.image.url)
            return primary.image.url

        # Fallback to first image
        first_image = obj.images.first()
        if first_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url

        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed product view."""

    current_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    stock_status = serializers.CharField(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    shop = ShopBasicSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    profit_margin = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True,
        required=False,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "short_description",
            "sku",
            "barcode",
            "price",
            "sale_price",
            "current_price",
            "stock_quantity",
            "stock_status",
            "is_in_stock",
            "is_low_stock",
            "weight_kg",
            "length_cm",
            "width_cm",
            "height_cm",
            "is_active",
            "is_featured",
            "meta_title",
            "meta_description",
            "view_count",
            "sales_count",
            "images",
            "shop",
            "category",
            "profit_margin",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "view_count",
            "sales_count",
            "created_at",
            "updated_at",
        ]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products."""

    class Meta:
        model = Product
        fields = [
            "shop",
            "category",
            "name",
            "slug",
            "description",
            "short_description",
            "sku",
            "barcode",
            "price",
            "sale_price",
            "cost_price",
            "stock_quantity",
            "min_stock_level",
            "max_stock_level",
            "weight_kg",
            "length_cm",
            "width_cm",
            "height_cm",
            "is_active",
            "is_featured",
            "meta_title",
            "meta_description",
        ]

    def validate(self, data):
        """Custom validation."""
        # Validate sale price is less than regular price
        if data.get("sale_price") and data.get("price"):
            if data["sale_price"] >= data["price"]:
                raise serializers.ValidationError(
                    {"sale_price": "Sale price must be less than regular price."}
                )

        # Validate stock levels
        if data.get("max_stock_level") and data.get("min_stock_level"):
            if data["max_stock_level"] <= data["min_stock_level"]:
                raise serializers.ValidationError(
                    {"max_stock_level": "Max stock level must be greater than min stock level."}
                )

        return data