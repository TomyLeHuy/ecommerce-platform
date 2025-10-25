"""API views for Orders app."""

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from src.customers.models import CustomerProfile
from src.merchants.models import MerchantProfile

from .models import Order, OrderStatusHistory
from .serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Order management."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return OrderCreateSerializer
        elif self.action == "retrieve":
            return OrderDetailSerializer
        return OrderListSerializer

    def get_queryset(self):
        """Filter orders based on user type."""
        user = self.request.user

        # Check if user is a merchant
        try:
            merchant_profile = MerchantProfile.objects.get(user=user)
            # Return orders for merchant's shop
            return Order.objects.filter(shop__merchant=merchant_profile).order_by(
                "-ordered_at"
            )
        except MerchantProfile.DoesNotExist:
            pass

        # Check if user is a customer
        try:
            customer_profile = CustomerProfile.objects.get(user=user)
            # Return orders for customer
            return Order.objects.filter(customer=customer_profile).order_by(
                "-ordered_at"
            )
        except CustomerProfile.DoesNotExist:
            # Return empty queryset if user is neither merchant nor customer
            return Order.objects.none()

    def create(self, request, *args, **kwargs):
        """Create a new order."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # Return detailed order information
        detail_serializer = OrderDetailSerializer(
            order, context={"request": request}
        )
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def my_orders(self, request):
        """Get current user's orders (customer view)."""
        try:
            customer_profile = CustomerProfile.objects.get(user=request.user)
            orders = Order.objects.filter(customer=customer_profile).order_by(
                "-ordered_at"
            )
            serializer = self.get_serializer(orders, many=True)
            return Response(serializer.data)
        except CustomerProfile.DoesNotExist:
            return Response(
                {"error": "Customer profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["get"])
    def merchant_orders(self, request):
        """Get orders for merchant's shop."""
        try:
            merchant_profile = MerchantProfile.objects.get(user=request.user)
            orders = Order.objects.filter(shop__merchant=merchant_profile).order_by(
                "-ordered_at"
            )
            serializer = self.get_serializer(orders, many=True)
            return Response(serializer.data)
        except MerchantProfile.DoesNotExist:
            return Response(
                {"error": "Merchant profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None):
        """Update order status (merchant only)."""
        order = self.get_object()

        # Check if user is the merchant who owns this order
        try:
            merchant_profile = MerchantProfile.objects.get(user=request.user)
            if order.shop.merchant != merchant_profile:
                return Response(
                    {"error": "You don't have permission to update this order"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except MerchantProfile.DoesNotExist:
            return Response(
                {"error": "Only merchants can update order status"},
                status=status.HTTP_403_FORBIDDEN,
            )

        new_status = request.data.get("status")
        notes = request.data.get("notes", "")

        if not new_status:
            return Response(
                {"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Validate status
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Valid options: {valid_statuses}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update order status
        old_status = order.status
        order.status = new_status

        # Update timestamp based on status
        if new_status == "confirmed" and not order.confirmed_at:
            order.confirmed_at = timezone.now()
        elif new_status == "shipped" and not order.shipped_at:
            order.shipped_at = timezone.now()
        elif new_status == "delivered" and not order.delivered_at:
            order.delivered_at = timezone.now()
        elif new_status == "cancelled" and not order.cancelled_at:
            order.cancelled_at = timezone.now()

        order.save()

        # Create status history entry
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            notes=notes or f"Status changed from {old_status} to {new_status}",
            changed_by=request.user.username,
        )

        serializer = OrderDetailSerializer(order, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["patch"])
    def update_tracking(self, request, pk=None):
        """Update tracking information (merchant only)."""
        order = self.get_object()

        # Check if user is the merchant who owns this order
        try:
            merchant_profile = MerchantProfile.objects.get(user=request.user)
            if order.shop.merchant != merchant_profile:
                return Response(
                    {"error": "You don't have permission to update this order"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except MerchantProfile.DoesNotExist:
            return Response(
                {"error": "Only merchants can update tracking information"},
                status=status.HTTP_403_FORBIDDEN,
            )

        tracking_number = request.data.get("tracking_number")
        tracking_url = request.data.get("tracking_url", "")

        if tracking_number:
            order.tracking_number = tracking_number
            order.tracking_url = tracking_url
            order.save()

            # Create status history entry
            OrderStatusHistory.objects.create(
                order=order,
                status=order.status,
                notes=f"Tracking number added: {tracking_number}",
                changed_by=request.user.username,
            )

        serializer = OrderDetailSerializer(order, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel an order (customer or merchant)."""
        order = self.get_object()

        # Check if order can be cancelled
        if not order.can_be_cancelled:
            return Response(
                {
                    "error": f"Order cannot be cancelled. Current status: {order.status}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check permissions
        is_customer = False
        is_merchant = False

        try:
            customer_profile = CustomerProfile.objects.get(user=request.user)
            if order.customer == customer_profile:
                is_customer = True
        except CustomerProfile.DoesNotExist:
            pass

        try:
            merchant_profile = MerchantProfile.objects.get(user=request.user)
            if order.shop.merchant == merchant_profile:
                is_merchant = True
        except MerchantProfile.DoesNotExist:
            pass

        if not (is_customer or is_merchant):
            return Response(
                {"error": "You don't have permission to cancel this order"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Cancel the order
        order.status = "cancelled"
        order.cancelled_at = timezone.now()
        order.save()

        # Create status history entry
        reason = request.data.get("reason", "No reason provided")
        OrderStatusHistory.objects.create(
            order=order,
            status="cancelled",
            notes=f"Order cancelled: {reason}",
            changed_by=request.user.username,
        )

        # Restore product stock
        for item in order.items.all():
            product = item.product
            product.stock_quantity += item.quantity
            product.sales_count -= item.quantity
            product.save()

        serializer = OrderDetailSerializer(order, context={"request": request})
        return Response(serializer.data)
