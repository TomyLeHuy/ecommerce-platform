"""API views for Customers app."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomerProfile, FavoriteShop, LoyaltyToken
from .serializers import (
    CustomerProfileSerializer,
    CustomerProfileUpdateSerializer,
    CustomerRegistrationSerializer,
    FavoriteShopSerializer,
    LoyaltyTokenSerializer,
)


class CustomerRegistrationViewSet(viewsets.GenericViewSet):
    """
    ViewSet for customer registration.

    POST /api/customers/register/ - Register new customer
    """

    permission_classes = [AllowAny]
    serializer_class = CustomerRegistrationSerializer

    @action(detail=False, methods=["post"])
    def register(self, request):
        """Register a new customer."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "message": "Registration successful! You are now logged in.",
            },
            status=status.HTTP_201_CREATED,
        )


class CustomerProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for customer profile management.

    GET /api/customers/profile/ - Get current user's profile
    PUT/PATCH /api/customers/profile/ - Update profile
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileSerializer

    def get_queryset(self):
        """Return only the current user's profile."""
        return CustomerProfile.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create profile for current user."""
        profile, created = CustomerProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile

    def get_serializer_class(self):
        """Use update serializer for PUT/PATCH."""
        if self.action in ["update", "partial_update"]:
            return CustomerProfileUpdateSerializer
        return CustomerProfileSerializer

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user's profile."""
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def token_balance(self, request):
        """Get current loyalty token balance."""
        profile = self.get_object()
        balance = LoyaltyToken.get_customer_balance(profile)
        return Response({"balance": balance})


class FavoriteShopViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing favorite shops.

    GET /api/customers/favorites/ - List favorite shops
    POST /api/customers/favorites/ - Add shop to favorites
    DELETE /api/customers/favorites/{id}/ - Remove from favorites
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteShopSerializer

    def get_queryset(self):
        """Return only current user's favorite shops."""
        profile, created = CustomerProfile.objects.get_or_create(
            user=self.request.user
        )
        return FavoriteShop.objects.filter(customer=profile).select_related(
            "shop", "shop__merchant"
        )

    def perform_create(self, serializer):
        """Set customer to current user's profile."""
        profile, created = CustomerProfile.objects.get_or_create(
            user=self.request.user
        )
        serializer.save(customer=profile)


class LoyaltyTokenViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing loyalty token transactions.

    GET /api/customers/tokens/ - List token transactions
    GET /api/customers/tokens/{id}/ - Transaction detail
    """

    permission_classes = [IsAuthenticated]
    serializer_class = LoyaltyTokenSerializer

    def get_queryset(self):
        """Return only current user's token transactions."""
        profile, created = CustomerProfile.objects.get_or_create(
            user=self.request.user
        )
        return LoyaltyToken.objects.filter(customer=profile).select_related("order")

    @action(detail=False, methods=["get"])
    def balance(self, request):
        """Get current token balance."""
        profile, created = CustomerProfile.objects.get_or_create(
            user=self.request.user
        )
        balance = LoyaltyToken.get_customer_balance(profile)
        return Response({"balance": balance})