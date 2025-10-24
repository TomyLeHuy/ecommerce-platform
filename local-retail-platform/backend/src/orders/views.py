"""API views for Orders app."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from src.customers.models import CustomerProfile
from .models import Order
from .serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for order management.

    GET /api/orders/ - List customer's orders
    POST /api/orders/ - Create new order
    GET /api/orders/{id}/ - Get order detail
    """

    permission_classes = [IsAuthenticated]
    lookup_field = "order_number"

    def get_queryset(self):
        """Return only current user's orders."""
        profile, created = CustomerProfile.objects.get_or_create(
            user=self.request.user
        )
        return (
            Order.objects.filter(customer=profile)
            .select_related("shop", "shop__merchant")
            .prefetch_related("items", "items__product", "status_history")
        )

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return OrderCreateSerializer
        elif self.action == "list":
            return OrderListSerializer
        return OrderDetailSerializer

    def create(self, request, *args, **kwargs):
        """Create a new order."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # Return detailed order info
        detail_serializer = OrderDetailSerializer(
            order, context={"request": request}
        )
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, order_number=None):
        """Cancel an order."""
        order = self.get_object()

        if not order.can_be_cancelled:
            return Response(
                {"error": "Order cannot be cancelled at this stage."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = "cancelled"
        order.save()

        # Create status history
        from .models import OrderStatusHistory

        OrderStatusHistory.objects.create(
            order=order,
            status="cancelled",
            notes="Cancelled by customer",
            changed_by=request.user.username,
        )

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """Get recent orders."""
        recent_orders = self.get_queryset()[:5]
        serializer = OrderListSerializer(
            recent_orders, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get order statistics."""
        profile, created = CustomerProfile.objects.get_or_create(
            user=request.user
        )
        orders = self.get_queryset()

        stats = {
            "total_orders": profile.total_orders,
            "total_spent": str(profile.total_spent),
            "pending_orders": orders.filter(status="pending").count(),
            "completed_orders": orders.filter(status="delivered").count(),
        }

        return Response(stats)