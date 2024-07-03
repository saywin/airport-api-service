from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from flights.models import (
    AirplaneType,
    Airport,
    Crew,
    Route,
    Flight,
    Airplane,
    Order,
    Ticket
)
from flights.serializers import OrderSerializer, OrderRetrieveSerializer

ORDER_URL = reverse("flights:order-list")


class BaseOrderTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.airplane_type = AirplaneType.objects.create(name="local")
        self.airport_1 = Airport.objects.create(
            name="Test Airport 1",
            closest_big_city="City 1"
        )
        self.airport_2 = Airport.objects.create(
            name="Test Airport 2",
            closest_big_city="City 2"
        )
        self.crew = Crew.objects.create(
            first_name="Join",
            last_name="Smith"
        )
        self.route = Route.objects.create(
            distance=1500,
            source=self.airport_1,
            destination=self.airport_2
        )
        self.airplane = Airplane.objects.create(
            name="Test Airplane",
            rows=30, seats_in_row=14,
            airplane_type=self.airplane_type,
        )
        self.flight = Flight.objects.create(
            departure_time=datetime.now(),
            arrival_time=datetime.now(),
            route=self.route,
            airplane=self.airplane
        )
        self.flight.crew.add(self.crew)


class UnAuthenticatedOrderTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderTest(BaseOrderTest):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            email="user@user.com",
            password="1qazcde3",
        )
        self.client.force_authenticate(user=self.user)

        tickets_data = [
            {"row": 1, "seat": 1, "flight": self.flight.id},
            {"row": 2, "seat": 3, "flight": self.flight.id},
        ]

        self.payload = {
            "created_at": datetime.now(),
            "user": self.user.id,
            "tickets": tickets_data,
        }

    def test_auth_required_user(self):
        response = self.client.get(ORDER_URL)
        order = Order.objects.all().select_related()
        serializer = OrderSerializer(order, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_route_detail_authenticated(self):
        order = Order.objects.create(
            user=self.user,
            created_at=datetime.now(),
        )
        ticket = Ticket.objects.create(
            row=4,
            seat=5,
            flight_id=self.flight.id,
            order=order)
        order.tickets.add(ticket)
        url = reverse("flights:order-detail", args=(order.id,))
        response = self.client.get(url)
        serializer = OrderRetrieveSerializer(order)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_order_user(self):
        response = self.client.post(
            ORDER_URL,
            self.payload,
            format="json"
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=response.data["id"])
        self.assertEqual(order.tickets.count(), 2)
