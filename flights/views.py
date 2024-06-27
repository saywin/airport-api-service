from django.db.models import Count, F
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
    FlightRetrieveSerializer, AirplaneRetrieveSerializer
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

        if self.action == "list":
            queryset = (
                Flight.objects.select_related()
                .prefetch_related("crew")
                .annotate(tickets_available=F(
                    "airplane__seats_in_row"
                ) * F("airplane__rows") - Count("tickets"))
            )
        if self.action == "retrieve":
            queryset = Flight.objects.select_related().prefetch_related("crew")
        return queryset


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneRetrieveSerializer
        return AirplaneSerializer

    @staticmethod
    def _params_to_ints(query_string: int) -> list[int]:
        return [int(str_id) for str_id in query_string.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        airplane_type = self.request.query_params.get("airplane_type")
        if self.action == "list":
            queryset = Airplane.objects.select_related()
        if airplane_type:
            airplane_type = self._params_to_ints(airplane_type)
            queryset = queryset.filter(airplane_type__id__in=airplane_type)
        return queryset.distinct()


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

    @staticmethod
    def _params_to_ints(query_string: int) -> list[int]:
        return [int(str_id) for str_id in query_string.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        if self.action == "list":
            queryset = Route.objects.select_related()

        if source:
            source = self._params_to_ints(source)
            queryset = queryset.filter(source__id__in=source)
        if destination:
            destination = self._params_to_ints(destination)
            queryset = queryset.filter(destination__id__in=destination)

        return queryset.distinct()


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        return CrewSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
