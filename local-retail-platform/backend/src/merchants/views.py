"""API views for Merchants app."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import MerchantProfile, Shop
from .serializers import MerchantProfileSerializer, ShopSerializer


class MerchantProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Merchant Profile management."""

    serializer_class = MerchantProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter to current user's merchant profile."""
        return MerchantProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user's merchant profile."""
        try:
            merchant_profile = MerchantProfile.objects.get(user=request.user)
            serializer = self.get_serializer(merchant_profile)
            return Response(serializer.data)
        except MerchantProfile.DoesNotExist:
            return Response(
                {"error": "Merchant profile not found. Please contact support."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Shop management."""

    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"

    def get_queryset(self):
        """Filter to current merchant's shops."""
        try:
            merchant_profile = MerchantProfile.objects.get(user=self.request.user)
            return Shop.objects.filter(merchant=merchant_profile)
        except MerchantProfile.DoesNotExist:
            return Shop.objects.none()

    @action(detail=False, methods=["get"])
    def my_shops(self, request):
        """Get all shops for the authenticated merchant."""
        try:
            merchant_profile = MerchantProfile.objects.get(user=request.user)
            shops = Shop.objects.filter(merchant=merchant_profile)
            serializer = self.get_serializer(shops, many=True)
            return Response(serializer.data)
        except MerchantProfile.DoesNotExist:
            return Response(
                {"error": "Merchant profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
