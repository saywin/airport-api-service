from django.urls import path, include
from rest_framework import routers

from flights.views import (
    AirplaneViewSet,
    FlightViewSet,
    AirportViewSet,
    AirplaneTypeViewSet,
    RouteViewSet,
    CrewViewSet,
    OrderViewSet
)

app_name = "flights"

router = routers.DefaultRouter()
router.register("airplanes", AirplaneViewSet)
router.register("flights", FlightViewSet)
router.register("airports", AirportViewSet)
router.register("airplane-types", AirplaneTypeViewSet)
router.register("routes", RouteViewSet)
router.register("crew", CrewViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
