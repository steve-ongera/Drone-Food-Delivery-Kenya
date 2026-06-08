from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class DeliveryZone(models.Model):
    """Geographic zone where drone delivery is available."""

    name = models.CharField(max_length=100)  # e.g. "Westlands", "Kilimani"
    county = models.CharField(max_length=100, default="Nairobi")
    is_active = models.BooleanField(default=True)
    max_drone_altitude_m = models.PositiveIntegerField(
        default=120,
        help_text="KCAA-permitted max altitude in metres for this zone",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius_km = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Serviceable radius from zone centre in km",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}, {self.county}"

    class Meta:
        ordering = ["name"]


class DroneOperator(models.Model):
    """Licensed drone logistics operator (e.g. Zipline, Astral Aerial)."""

    FOCUS_MEDICAL = "medical"
    FOCUS_FOOD = "food"
    FOCUS_AGRICULTURAL = "agricultural"
    FOCUS_GENERAL = "general"

    FOCUS_CHOICES = [
        (FOCUS_MEDICAL, "Medical & Healthcare"),
        (FOCUS_FOOD, "Food & Beverage"),
        (FOCUS_AGRICULTURAL, "Agricultural"),
        (FOCUS_GENERAL, "General Cargo"),
    ]

    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    kcaa_license_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Kenya Civil Aviation Authority certification number",
    )
    primary_focus = models.CharField(
        max_length=20, choices=FOCUS_CHOICES, default=FOCUS_GENERAL
    )
    headquarters = models.CharField(max_length=150)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    bvlos_certified = models.BooleanField(
        default=False,
        help_text="Certified for Beyond Visual Line of Sight operations",
    )
    zones = models.ManyToManyField(
        DeliveryZone,
        related_name="operators",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Drone(models.Model):
    """Individual drone asset belonging to an operator."""

    STATUS_IDLE = "idle"
    STATUS_IN_FLIGHT = "in_flight"
    STATUS_CHARGING = "charging"
    STATUS_MAINTENANCE = "maintenance"

    STATUS_CHOICES = [
        (STATUS_IDLE, "Idle"),
        (STATUS_IN_FLIGHT, "In Flight"),
        (STATUS_CHARGING, "Charging"),
        (STATUS_MAINTENANCE, "Under Maintenance"),
    ]

    operator = models.ForeignKey(
        DroneOperator, on_delete=models.CASCADE, related_name="drones"
    )
    serial_number = models.CharField(max_length=100, unique=True)
    model_name = models.CharField(max_length=100)
    max_payload_kg = models.DecimalField(max_digits=5, decimal_places=2)
    max_range_km = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_IDLE
    )
    battery_level = models.PositiveSmallIntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Battery percentage 0–100",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.model_name} [{self.serial_number}]"

    class Meta:
        ordering = ["operator", "serial_number"]


class MenuItem(models.Model):
    """Food item available for drone delivery."""

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price_kes = models.DecimalField(
        max_digits=8, decimal_places=2, help_text="Price in Kenyan Shillings"
    )
    weight_kg = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        help_text="Item weight in kg (used to check drone payload limits)",
    )
    is_available = models.BooleanField(default=True)
    operator = models.ForeignKey(
        DroneOperator, on_delete=models.CASCADE, related_name="menu_items"
    )
    image = models.ImageField(upload_to="menu/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} — KES {self.price_kes}"

    class Meta:
        ordering = ["name"]


class Order(models.Model):
    """A customer drone delivery order."""

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_PREPARING = "preparing"
    STATUS_IN_FLIGHT = "in_flight"
    STATUS_DELIVERED = "delivered"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_PREPARING, "Preparing"),
        (STATUS_IN_FLIGHT, "In Flight"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_FAILED, "Failed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    customer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="orders"
    )
    operator = models.ForeignKey(
        DroneOperator, on_delete=models.PROTECT, related_name="orders"
    )
    drone = models.ForeignKey(
        Drone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    delivery_zone = models.ForeignKey(
        DeliveryZone, on_delete=models.PROTECT, related_name="orders"
    )

    # Delivery location
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    delivery_address = models.TextField()

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )

    # Financials
    subtotal_kes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee_kes = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_kes = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Tracking
    estimated_delivery_minutes = models.PositiveIntegerField(null=True, blank=True)
    actual_delivery_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} — {self.customer} [{self.status}]"

    class Meta:
        ordering = ["-created_at"]


class OrderItem(models.Model):
    """A single line item within an Order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit_price_kes = models.DecimalField(max_digits=8, decimal_places=2)

    def get_total(self):
        return self.quantity * self.unit_price_kes

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} (Order #{self.order_id})"

    class Meta:
        ordering = ["menu_item"]