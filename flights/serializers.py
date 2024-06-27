from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from flights.models import (
    Airport,
    Airplane,
    Route,
    Flight,
    Crew,
    Ticket,
    Order,
    AirplaneType
)


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name",)


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "route",
            "airplane",
            "crew"
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class CrewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "full_name")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "distance", "source", "destination")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(read_only=True, slug_field="name")
    destination = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )


class FlightListSerializer(FlightSerializer):
    airplane = serializers.SlugRelatedField(read_only=True, slug_field="name")
    crew = serializers.SlugRelatedField(
        read_only=True,
        slug_field="full_name",
        many=True,
    )
    route = RouteListSerializer()


class FlightRetrieveSerializer(FlightSerializer):
    route = RouteListSerializer()
    airplane = AirplaneSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True)
    taken_seats = serializers.SerializerMethodField()

    def get_taken_seats(self, obj):
        tickets = Ticket.objects.filter(flight=obj)
        return [{"row": ticket.row, "seat": ticket.seat} for ticket in tickets]

    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "route",
            "airplane",
            "crew",
            "taken_seats"
        )


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.CharField(
        source="airplane_type.name",
        read_only=True
    )


class AirplaneRetrieveSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer()


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")

    def validate(self, attrs):
        Ticket.validate_ticket(
            row=attrs["row"],
            seat=attrs["seat"],
            airplane=attrs["flight"],
            error_to_raise=serializers.ValidationError
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order

