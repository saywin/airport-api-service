from rest_framework import serializers

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


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "distance", "source", "destination")


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
        fields = ("id", "first_name", "last_name")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "created_at")
