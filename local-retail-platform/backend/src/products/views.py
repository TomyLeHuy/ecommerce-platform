"""API views for Products app."""

from decimal import Decimal

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Category, Product, ProductImage
from .serializers import (
    CategorySerializer,
    ProductCreateUpdateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for browsing product categories.

    GET /api/products/categories/ - List all categories
    GET /api/products/categories/{id}/ - Get category detail
    """

    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["display_order", "name"]
    ordering = ["display_order", "name"]

    @action(detail=False, methods=["get"])
    def root(self, request):
        """Get only root (parent-less) categories."""
        root_categories = self.queryset.filter(parent__isnull=True)
        serializer = self.get_serializer(root_categories, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product management and browsing.

    Public endpoints (AllowAny):
    - GET /api/products/products/ - List products
    - GET /api/products/products/{id}/ - Product detail
    - GET /api/products/products/search_nearby/ - Geo-based search

    Merchant endpoints (IsAuthenticated):
    - POST /api/products/products/ - Create product
    - PUT/PATCH /api/products/products/{id}/ - Update product
    - DELETE /api/products/products/{id}/ - Delete product
    """

    queryset = Product.objects.select_related(
        "shop",
        "shop__merchant",
        "category",
    ).prefetch_related("images").filter(is_active=True)

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {
        "category": ["exact"],
        "shop": ["exact"],
        "price": ["gte", "lte"],
        "is_featured": ["exact"],
    }
    search_fields = ["name", "description", "short_description", "sku"]
    ordering_fields = ["price", "created_at", "sales_count", "name"]
    ordering = ["-created_at"]
    lookup_field = "slug"

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return ProductListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        """Allow public read access, require auth for write operations."""
        if self.action in ["list", "retrieve", "search_nearby"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        """Increment view count when product is viewed."""
        instance = self.get_object()

        # Increment view count
        Product.objects.filter(pk=instance.pk).update(
            view_count=instance.view_count + 1
        )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def search_nearby(self, request):
        """
        Search products by geographic proximity (core "Tinder" feature).

        Query params:
        - latitude (required): Center latitude
        - longitude (required): Center longitude
        - radius_km (optional): Search radius in km (default: 150, max: 500)
        - category: Filter by category slug
        - min_price: Minimum price
        - max_price: Maximum price
        - search: Text search in name/description
        """
        # Get location parameters
        try:
            latitude = Decimal(request.query_params.get("latitude"))
            longitude = Decimal(request.query_params.get("longitude"))
        except (TypeError, ValueError):
            return Response(
                {"error": "Valid latitude and longitude parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get radius (default 150km, max 500km)
        try:
            radius_km = int(request.query_params.get("radius_km", 150))
            radius_km = min(radius_km, 500)  # Cap at 500km
        except ValueError:
            radius_km = 150

        # TODO: Implement actual geo-spatial query using PostGIS
        # For now, return all products (placeholder)
        # When PostGIS is enabled, use ST_DWithin for efficient geo-queries

        queryset = self.filter_queryset(self.get_queryset())

        # Apply additional filters
        category_slug = request.query_params.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        min_price = request.query_params.get("min_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        max_price = request.query_params.get("max_price")
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        search_query = request.query_params.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(short_description__icontains=search_query)
            )

        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(
                page,
                many=True,
                context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(
            queryset,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def featured(self, request):
        """Get featured products."""
        featured_products = self.get_queryset().filter(is_featured=True)[:20]
        serializer = ProductListSerializer(
            featured_products,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def related(self, request, slug=None):
        """Get related products from same category."""
        product = self.get_object()
        related = (
            self.get_queryset()
            .filter(category=product.category)
            .exclude(pk=product.pk)[:8]
        )
        serializer = ProductListSerializer(
            related,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_products(self, request):
        """Get products for authenticated merchant's shops."""
        if not hasattr(request.user, "merchant_profile"):
            return Response(
                {"error": "User is not a merchant."},
                status=status.HTTP_403_FORBIDDEN,
            )

        merchant_shops = request.user.merchant_profile.shops.all()
        products = Product.objects.filter(shop__in=merchant_shops)

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(
                page,
                many=True,
                context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(
            products,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)