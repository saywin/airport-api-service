from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from flights.models import Flight, Crew, Airplane, Route, AirplaneType, Airport
from flights.serializers import FlightListSerializer, FlightRetrieveSerializer


class BaseFlightAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.airport_1 = Airport.objects.create(
            name="Airport Test",
            closest_big_city="City test"
        )

        self.airport_2 = Airport.objects.create(
            name="Airport Test 2",
            closest_big_city="City test 2"
        )

        self.route = Route.objects.create(
            distance=1000,
            source=self.airport_1,
            destination=self.airport_2
        )
        self.type_1 = AirplaneType.objects.create(name="Type 1")
        self.airplane = Airplane.objects.create(
            name="Test Airplane",
            rows=50,
            seats_in_row=6,
            airplane_type=self.type_1
        )
        self.crew = Crew.objects.create(
            first_name="John",
            last_name="Smith"
        )

        self.flight = Flight.objects.create(
            departure_time=datetime.now(),
            arrival_time=datetime.now(),
            route=self.route,
            airplane=self.airplane
        )
        self.flight.crew.add(self.crew)
        self.list_url = reverse("flights:flight-list")
        self.detail_url = reverse(
            "flights:flight-detail", args=[self.flight.id]
        )

        self.payload = {
            "departure_time": datetime.now(),
            "arrival_time": datetime.now(),
            "route": self.route.id,
            "airplane": self.airplane.id,
            "crew": (self.crew.id,)
        }


class UnAuthenticatedFlightApiTest(BaseFlightAPITest):
    def test_get_flight_list_unauthorized(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_flight_detail_unauthorized(self):
        detail_url = self.detail_url
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTest(BaseFlightAPITest):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            email="user@user.com", password="1qazcde3"
        )
        self.client.force_authenticate(user=self.user)

    def test_auth_required_user(self):
        response = self.client.get(self.list_url)
        flight = Flight.objects.all().select_related().annotate(
            tickets_available=F("airplane__seats_in_row")
            * F("airplane__rows")
            - Count("tickets")
        )
        serializer = FlightListSerializer(flight, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flight_detail_authenticated(self):
        response = self.client.get(self.detail_url)
        serializer = FlightRetrieveSerializer(self.flight)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_create_flight_forbidden(self):
        response = self.client.post(self.list_url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightAPITest(BaseFlightAPITest):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="1qazcde3",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_flight_admin(self):
        response = self.client.post(self.list_url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_flight_admin(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
