"""API serializers for Customers app."""

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import CustomerProfile, FavoriteShop, LoyaltyToken


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id"]


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for customer registration."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
        ]

    def validate(self, attrs):
        """Validate passwords match and email is unique."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )

        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError(
                {"email": "A user with this email already exists."}
            )

        return attrs

    def create(self, validated_data):
        """Create user and customer profile."""
        validated_data.pop("password_confirm")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )

        # Create customer profile
        CustomerProfile.objects.create(user=user)

        return user


class CustomerProfileSerializer(serializers.ModelSerializer):
    """Serializer for CustomerProfile."""

    user = UserSerializer(read_only=True)
    token_balance = serializers.SerializerMethodField()
    has_location = serializers.BooleanField(read_only=True)
    has_complete_profile = serializers.BooleanField(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = [
            "id",
            "user",
            "phone",
            "date_of_birth",
            "street_address",
            "city",
            "postal_code",
            "country",
            "latitude",
            "longitude",
            "default_search_radius_km",
            "newsletter_subscribed",
            "marketing_consent",
            "total_orders",
            "total_spent",
            "token_balance",
            "has_location",
            "has_complete_profile",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "total_orders",
            "total_spent",
            "created_at",
            "updated_at",
        ]

    def get_token_balance(self, obj):
        """Get current loyalty token balance."""
        return LoyaltyToken.get_customer_balance(obj)


class CustomerProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating customer profile."""

    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    email = serializers.EmailField(source="user.email", required=False)

    class Meta:
        model = CustomerProfile
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "date_of_birth",
            "street_address",
            "city",
            "postal_code",
            "country",
            "latitude",
            "longitude",
            "default_search_radius_km",
            "newsletter_subscribed",
            "marketing_consent",
        ]

    def update(self, instance, validated_data):
        """Update both user and profile."""
        user_data = validated_data.pop("user", {})

        # Update user fields
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class FavoriteShopSerializer(serializers.ModelSerializer):
    """Serializer for FavoriteShop."""

    shop_name = serializers.CharField(source="shop.name", read_only=True)
    shop_slug = serializers.CharField(source="shop.slug", read_only=True)
    shop_city = serializers.CharField(source="shop.merchant.city", read_only=True)

    class Meta:
        model = FavoriteShop
        fields = [
            "id",
            "shop",
            "shop_name",
            "shop_slug",
            "shop_city",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class LoyaltyTokenSerializer(serializers.ModelSerializer):
    """Serializer for LoyaltyToken transactions."""

    token_value_euros = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = LoyaltyToken
        fields = [
            "id",
            "transaction_type",
            "amount",
            "balance_after",
            "order",
            "description",
            "token_value_euros",
            "created_at",
        ]
        read_only_fields = ["id", "balance_after", "created_at"]