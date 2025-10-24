"""URL routing for Orders API."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet

app_name = "orders"

# Create router
router = DefaultRouter()
router.register(r"", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
]