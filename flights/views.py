from django.db.models import Count, F
from django.http import HttpRequest
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
    FlightRetrieveSerializer,
    AirplaneRetrieveSerializer,
    OrderRetrieveSerializer, AirplaneImageSerializer
)
from user.permissions import IsAdminAllOrIsAuthenticatedReadOnly


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    permission_classes = [IsAdminAllOrIsAuthenticatedReadOnly,]

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
    permission_classes = [IsAdminAllOrIsAuthenticatedReadOnly, ]

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneRetrieveSerializer
        if self.action == "upload_image":
            return AirplaneImageSerializer
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

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None) -> Response:
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAdminAllOrIsAuthenticatedReadOnly, ]


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [IsAdminAllOrIsAuthenticatedReadOnly, ]


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    permission_classes = [IsAdminAllOrIsAuthenticatedReadOnly, ]

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
    permission_classes = [IsAdminAllOrIsAuthenticatedReadOnly, ]
    queryset = Crew.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        return CrewSerializer


class OrderSetPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = "page_size"
    max_page_size = 20


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    pagination_class = OrderSetPagination
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "retrieve":
            queryset = Order.objects.prefetch_related(
                "tickets__flight__airplane",
                "tickets__flight__crew",
                "tickets__flight__route",
            )
        if self.action == "list":
            queryset = Order.objects.prefetch_related("tickets")
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderRetrieveSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
