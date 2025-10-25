"""URL routing for Merchants API."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MerchantProfileViewSet, ShopViewSet

app_name = "merchants"

# Create router
router = DefaultRouter()
router.register(r"profile", MerchantProfileViewSet, basename="merchant-profile")
router.register(r"shops", ShopViewSet, basename="shop")

urlpatterns = [
    path("", include(router.urls)),
]
