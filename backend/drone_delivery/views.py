from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import DeliveryZone, DroneOperator, Drone, MenuItem, Order
from .serializers import (
    DeliveryZoneSerializer,
    DroneOperatorListSerializer,
    DroneOperatorDetailSerializer,
    DroneSerializer,
    MenuItemSerializer,
    OrderReadSerializer,
    OrderWriteSerializer,
    OrderStatusUpdateSerializer,
)
from .permissions import IsOperatorOrReadOnly, IsOrderOwnerOrOperator


# ---------------------------------------------------------------------------
# DeliveryZone
# ---------------------------------------------------------------------------

class DeliveryZoneViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List and retrieve delivery zones.
    Only active zones are shown to the public.
    """

    queryset = DeliveryZone.objects.filter(is_active=True)
    serializer_class = DeliveryZoneSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "county"]


# ---------------------------------------------------------------------------
# DroneOperator
# ---------------------------------------------------------------------------

class DroneOperatorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List and retrieve drone operators.
    Supports filtering by focus area and BVLOS certification.
    """

    queryset = DroneOperator.objects.filter(is_active=True).prefetch_related("zones")
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["primary_focus", "bvlos_certified"]
    search_fields = ["name", "headquarters"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DroneOperatorDetailSerializer
        return DroneOperatorListSerializer

    @action(detail=True, methods=["get"], url_path="menu")
    def menu(self, request, pk=None):
        """Return all available menu items for this operator."""
        operator = self.get_object()
        items = operator.menu_items.filter(is_available=True)
        serializer = MenuItemSerializer(items, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="drones")
    def drones(self, request, pk=None):
        """Return all drones for this operator (staff only)."""
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        operator = self.get_object()
        serializer = DroneSerializer(operator.drones.all(), many=True)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# Drone
# ---------------------------------------------------------------------------

class DroneViewSet(viewsets.ModelViewSet):
    """
    CRUD for drones. Restricted to staff users.
    """

    queryset = Drone.objects.select_related("operator").all()
    serializer_class = DroneSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["operator", "status"]


# ---------------------------------------------------------------------------
# MenuItem
# ---------------------------------------------------------------------------

class MenuItemViewSet(viewsets.ModelViewSet):
    """
    List available menu items. Write operations restricted to operator staff.
    """

    queryset = MenuItem.objects.filter(is_available=True).select_related("operator")
    serializer_class = MenuItemSerializer
    permission_classes = [IsOperatorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["operator", "is_available"]
    search_fields = ["name", "description"]


# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------

class OrderViewSet(viewsets.ModelViewSet):
    """
    Create and manage delivery orders.

    - Customers see only their own orders.
    - Staff see all orders.
    - Status updates use a dedicated PATCH endpoint.
    """

    permission_classes = [permissions.IsAuthenticated, IsOrderOwnerOrOperator]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "operator", "delivery_zone"]
    ordering_fields = ["created_at", "total_kes"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related(
            "customer", "operator", "drone", "delivery_zone"
        ).prefetch_related("items__menu_item")

        if user.is_staff:
            return qs
        return qs.filter(customer=user)

    def get_serializer_class(self):
        if self.action in ["create"]:
            return OrderWriteSerializer
        if self.action in ["partial_update", "update_status"]:
            return OrderStatusUpdateSerializer
        return OrderReadSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        """
        Dedicated endpoint for operators/staff to update order status and assign a drone.
        PATCH /api/orders/{id}/status/
        """
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff can update order status."},
                status=status.HTTP_403_FORBIDDEN,
            )
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderReadSerializer(order, context={"request": request}).data)

    @action(detail=False, methods=["get"], url_path="my-orders")
    def my_orders(self, request):
        """Shortcut: return the current user's orders."""
        orders = Order.objects.filter(customer=request.user).select_related(
            "operator", "delivery_zone"
        ).prefetch_related("items__menu_item")
        serializer = OrderReadSerializer(orders, many=True, context={"request": request})
        return Response(serializer.data)