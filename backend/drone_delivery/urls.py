from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DeliveryZoneViewSet,
    DroneOperatorViewSet,
    DroneViewSet,
    MenuItemViewSet,
    OrderViewSet,
)

router = DefaultRouter()
router.register(r"zones", DeliveryZoneViewSet, basename="zone")
router.register(r"operators", DroneOperatorViewSet, basename="operator")
router.register(r"drones", DroneViewSet, basename="drone")
router.register(r"menu-items", MenuItemViewSet, basename="menuitem")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
]