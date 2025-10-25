"""API serializers for Merchants app."""

from rest_framework import serializers

from .models import MerchantProfile, Shop, Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription."""

    commission_rate = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )
    monthly_fee = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    is_premium = serializers.BooleanField(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "tier",
            "status",
            "commission_rate",
            "monthly_fee",
            "is_premium",
            "premium_start_date",
            "premium_end_date",
        ]
        read_only_fields = ["id"]


class ShopSerializer(serializers.ModelSerializer):
    """Serializer for Shop."""

    is_operational = serializers.BooleanField(read_only=True)

    class Meta:
        model = Shop
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "logo",
            "banner_image",
            "email",
            "phone",
            "delivery_radius_km",
            "accepts_online_orders",
            "accepts_in_store_pickup",
            "total_products",
            "total_orders",
            "is_active",
            "is_operational",
        ]
        read_only_fields = ["id", "total_products", "total_orders"]


class MerchantProfileSerializer(serializers.ModelSerializer):
    """Serializer for Merchant Profile."""

    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    shops = ShopSerializer(many=True, read_only=True)
    subscription = SubscriptionSerializer(read_only=True)

    class Meta:
        model = MerchantProfile
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "company_name",
            "tax_id",
            "phone",
            "business_street_address",
            "business_city",
            "business_postal_code",
            "business_country",
            "is_verified",
            "shops",
            "subscription",
        ]
        read_only_fields = ["id", "is_verified"]
