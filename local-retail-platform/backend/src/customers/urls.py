"""URL routing for Customers API."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomerProfileViewSet,
    CustomerRegistrationViewSet,
    FavoriteShopViewSet,
    LoyaltyTokenViewSet,
)

app_name = "customers"

# Create router
router = DefaultRouter()
router.register(r"profile", CustomerProfileViewSet, basename="profile")
router.register(r"favorites", FavoriteShopViewSet, basename="favorite")
router.register(r"tokens", LoyaltyTokenViewSet, basename="token")

urlpatterns = [
    # Registration endpoint (non-standard router endpoint)
    path("register/", CustomerRegistrationViewSet.as_view({"post": "register"}), name="register"),

    # Include router URLs
    path("", include(router.urls)),
]