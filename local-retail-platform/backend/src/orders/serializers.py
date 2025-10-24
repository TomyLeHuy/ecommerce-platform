"""API serializers for Orders app."""

from decimal import Decimal

from rest_framework import serializers

from src.customers.models import CustomerProfile
from src.products.models import Product
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem."""

    product_id = serializers.IntegerField(write_only=True)
    product_name = serializers.CharField(read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_id",
            "product_name",
            "product_sku",
            "product_image",
            "unit_price",
            "quantity",
            "line_total",
            "tax_rate",
            "tax_amount",
        ]
        read_only_fields = ["id", "product_name", "product_sku", "line_total", "tax_amount"]

    def get_product_image(self, obj):
        """Get product primary image."""
        primary_image = obj.product.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders."""

    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "shipping_street_address",
            "shipping_city",
            "shipping_postal_code",
            "shipping_country",
            "customer_notes",
            "items",
        ]

    def validate_items(self, items):
        """Validate order items."""
        if not items:
            raise serializers.ValidationError("Order must contain at least one item.")

        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 0)

            if quantity <= 0:
                raise serializers.ValidationError("Item quantity must be greater than 0.")

            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {product_id} not found.")

            if not product.is_in_stock:
                raise serializers.ValidationError(f"Product '{product.name}' is out of stock.")

            if product.stock_quantity < quantity:
                raise serializers.ValidationError(
                    f"Product '{product.name}' has only {product.stock_quantity} items in stock."
                )

        return items

    def create(self, validated_data):
        """Create order with items."""
        items_data = validated_data.pop("items")
        request = self.context.get("request")

        # Get or create customer profile
        customer_profile, created = CustomerProfile.objects.get_or_create(
            user=request.user
        )

        # Create order
        order = Order.objects.create(
            customer=customer_profile,
            shop=items_data[0]["product_id"]
            and Product.objects.get(id=items_data[0]["product_id"]).shop,
            **validated_data,
        )

        # Calculate totals
        subtotal = Decimal("0.00")

        # Create order items
        for item_data in items_data:
            product_id = item_data.pop("product_id")
            product = Product.objects.get(id=product_id)

            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                unit_price=product.current_price,
                quantity=item_data["quantity"],
            )

            subtotal += order_item.line_total

            # Update product stock
            product.stock_quantity -= item_data["quantity"]
            product.sales_count += item_data["quantity"]
            product.save()

        # Calculate order totals
        tax_rate = Decimal("0.19")  # 19% VAT
        tax_amount = subtotal * tax_rate

        # Simple shipping calculation
        shipping_cost = Decimal("0.00") if subtotal >= 50 else Decimal("4.99")

        order.subtotal = subtotal
        order.tax_amount = tax_amount
        order.shipping_cost = shipping_cost
        order.total = subtotal + tax_amount + shipping_cost
        order.save()

        # Update customer stats
        customer_profile.total_orders += 1
        customer_profile.total_spent += order.total
        customer_profile.save()

        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status="pending",
            notes="Order placed",
            changed_by=request.user.username,
        )

        return order


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for order list view."""

    shop_name = serializers.CharField(source="shop.name", read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "shop_name",
            "status",
            "total",
            "item_count",
            "ordered_at",
            "payment_status",
        ]

    def get_item_count(self, obj):
        """Get total number of items in order."""
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed order view."""

    shop = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "shop",
            "status",
            "fulfillment_method",
            "shipping_street_address",
            "shipping_city",
            "shipping_postal_code",
            "shipping_country",
            "subtotal",
            "tax_amount",
            "shipping_cost",
            "discount_amount",
            "tokens_used",
            "tokens_value",
            "total",
            "payment_status",
            "payment_method",
            "customer_notes",
            "tracking_number",
            "tracking_url",
            "items",
            "status_history",
            "ordered_at",
            "confirmed_at",
            "shipped_at",
            "delivered_at",
            "cancelled_at",
        ]

    def get_shop(self, obj):
        """Get shop information."""
        return {
            "id": obj.shop.id,
            "name": obj.shop.name,
            "slug": obj.shop.slug,
            "merchant_name": obj.shop.merchant.company_name,
            "email": obj.shop.email,
            "phone": obj.shop.phone,
        }

    def get_status_history(self, obj):
        """Get order status history."""
        history = obj.status_history.all()[:5]  # Last 5 status changes
        return [
            {
                "status": h.status,
                "notes": h.notes,
                "changed_by": h.changed_by,
                "created_at": h.created_at,
            }
            for h in history
        ]