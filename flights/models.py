from django.conf import settings
from django.db import models


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        "AirplaneType",
        on_delete=models.CASCADE,
        related_name="airplanes"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.airplane_type.name})"


class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey("Flight", on_delete=models.CASCADE)
    order = models.ForeignKey("Order", on_delete=models.CASCADE)

    class Meta:
        ordering = ["flight", "row", "seat"]

    def __str__(self):
        return f"{self.row} {self.seat} {self.flight}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at}"


class Route(models.Model):
    distance = models.IntegerField()
    source = models.ForeignKey(
        "Airport",
        on_delete=models.CASCADE,
        related_name="source-routes"
    )
    destination = models.ForeignKey(
        "Airport",
        on_delete=models.CASCADE,
        related_name="destination-routes"
    )

    class Meta:
        ordering = ["source__name", "destination__name"]

    def __str__(self):
        return f"{self.source} {self.destination}"


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Flight(models.Model):
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    crew = models.ManyToManyField("Crew", related_name="flights")

    class Meta:
        ordering = ["departure_time"]

    def __str__(self):
        return (
            f"{self.route.name} "
            f"{self.airplane.name} "
            f"{self.departure_time} "
            f"{self.arrival_time}"
        )


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
