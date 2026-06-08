from rest_framework import serializers
from django.contrib.auth.models import User
from .models import DeliveryZone, DroneOperator, Drone, MenuItem, Order, OrderItem


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id"]


# ---------------------------------------------------------------------------
# DeliveryZone
# ---------------------------------------------------------------------------

class DeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryZone
        fields = [
            "id",
            "name",
            "county",
            "is_active",
            "max_drone_altitude_m",
            "latitude",
            "longitude",
            "radius_km",
        ]


# ---------------------------------------------------------------------------
# DroneOperator
# ---------------------------------------------------------------------------

class DroneOperatorListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""

    zones = DeliveryZoneSerializer(many=True, read_only=True)

    class Meta:
        model = DroneOperator
        fields = [
            "id",
            "name",
            "slug",
            "primary_focus",
            "headquarters",
            "website",
            "is_active",
            "bvlos_certified",
            "zones",
        ]


class DroneOperatorDetailSerializer(DroneOperatorListSerializer):
    """Full serializer including drone count for detail view."""

    drone_count = serializers.SerializerMethodField()

    class Meta(DroneOperatorListSerializer.Meta):
        fields = DroneOperatorListSerializer.Meta.fields + [
            "kcaa_license_number",
            "drone_count",
            "created_at",
        ]

    def get_drone_count(self, obj):
        return obj.drones.count()


# ---------------------------------------------------------------------------
# Drone
# ---------------------------------------------------------------------------

class DroneSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source="operator.name", read_only=True)

    class Meta:
        model = Drone
        fields = [
            "id",
            "operator",
            "operator_name",
            "serial_number",
            "model_name",
            "max_payload_kg",
            "max_range_km",
            "status",
            "battery_level",
        ]
        read_only_fields = ["operator_name"]


# ---------------------------------------------------------------------------
# MenuItem
# ---------------------------------------------------------------------------

class MenuItemSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source="operator.name", read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "operator",
            "operator_name",
            "name",
            "description",
            "price_kes",
            "weight_kg",
            "is_available",
            "image",
        ]
        read_only_fields = ["operator_name"]


# ---------------------------------------------------------------------------
# OrderItem
# ---------------------------------------------------------------------------

class OrderItemReadSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    total_kes = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "quantity", "unit_price_kes", "total_kes"]

    def get_total_kes(self, obj):
        return obj.get_total()


class OrderItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["menu_item", "quantity"]


# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------

class OrderReadSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    operator = DroneOperatorListSerializer(read_only=True)
    delivery_zone = DeliveryZoneSerializer(read_only=True)
    drone = DroneSerializer(read_only=True)
    items = OrderItemReadSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "operator",
            "drone",
            "delivery_zone",
            "delivery_latitude",
            "delivery_longitude",
            "delivery_address",
            "status",
            "status_display",
            "items",
            "subtotal_kes",
            "delivery_fee_kes",
            "total_kes",
            "estimated_delivery_minutes",
            "actual_delivery_at",
            "notes",
            "created_at",
            "updated_at",
        ]


class OrderWriteSerializer(serializers.ModelSerializer):
    """Used for creating a new order."""

    items = OrderItemWriteSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = [
            "operator",
            "delivery_zone",
            "delivery_latitude",
            "delivery_longitude",
            "delivery_address",
            "items",
            "notes",
        ]

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("An order must contain at least one item.")
        return items

    def validate(self, data):
        # Check that all items belong to the chosen operator
        operator = data.get("operator")
        for item_data in data.get("items", []):
            menu_item = item_data["menu_item"]
            if menu_item.operator != operator:
                raise serializers.ValidationError(
                    f"Menu item '{menu_item.name}' does not belong to the selected operator."
                )
            if not menu_item.is_available:
                raise serializers.ValidationError(
                    f"Menu item '{menu_item.name}' is currently unavailable."
                )
        return data

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        request = self.context.get("request")
        validated_data["customer"] = request.user if request else None

        subtotal = sum(
            item["menu_item"].price_kes * item["quantity"] for item in items_data
        )
        delivery_fee = 150  # flat KES 150 delivery fee
        validated_data["subtotal_kes"] = subtotal
        validated_data["delivery_fee_kes"] = delivery_fee
        validated_data["total_kes"] = subtotal + delivery_fee

        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(
                order=order,
                menu_item=item_data["menu_item"],
                quantity=item_data["quantity"],
                unit_price_kes=item_data["menu_item"].price_kes,
            )
        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Only allows patching the status and drone fields."""

    class Meta:
        model = Order
        fields = ["status", "drone", "estimated_delivery_minutes", "actual_delivery_at"]