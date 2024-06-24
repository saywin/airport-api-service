from rest_framework import viewsets

from flights.models import (
    Airport,
    Flight,
    AirplaneType,
    Route,
    Crew,
    Airplane,
    Order
)
from flights.serializers import (
    AirportSerializer,
    FlightSerializer,
    AirplaneTypeSerializer,
    RouteSerializer,
    CrewSerializer,
    AirplaneSerializer,
    OrderSerializer,
    FlightListSerializer,
    CrewListSerializer,
    RouteListSerializer,
    AirplaneListSerializer,
    FlightRetrieveSerializer
)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            queryset = Flight.objects.select_related().prefetch_related("crew")
        return queryset


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        return AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = Airplane.objects.select_related()
        return queryset


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        return RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = Route.objects.select_related()
        return queryset


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        return CrewSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
