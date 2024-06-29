from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from flights.models import AirplaneType, Airplane
from flights.serializers import (
    AirplaneListSerializer,
    AirplaneRetrieveSerializer
)

AIRPLANE_URL = reverse("flights:airplane-list")


def sample_airplane(**params):
    airplane_type = AirplaneType.objects.create(name="local")
    defaults = {
        "name": "Ty 123",
        "rows": 10,
        "seats_in_row": 10,
        "airplane_type": airplane_type
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


class UnAuthenticatedAirplaneApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@user.com",
            password="1qazcde3",
        )
        self.client.force_authenticate(user=self.user)
        self.type_1 = AirplaneType.objects.create(name="local")
        self.type_2 = AirplaneType.objects.create(name="international")
        self.airplane1 = Airplane.objects.create(
            name="Airplane 1",
            airplane_type=self.type_1,
            rows=12,
            seats_in_row=8
        )
        self.airplane2 = Airplane.objects.create(
            name="Airplane 2",
            airplane_type=self.type_2,
            rows=38,
            seats_in_row=10
        )

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_airplane_list_without_filter(self):
        url = AIRPLANE_URL
        response = self.client.get(url)
        airplanes = Airplane.objects.all().select_related()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_list_airplanes_with_type_filter(self):
        url = AIRPLANE_URL + "?airplane_type=1"
        response = self.client.get(url)

        airplanes = Airplane.objects.filter(
            airplane_type__id=1).select_related("airplane_type")
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_airplane(self):
        url = reverse("flights:airplane-detail", args=(self.airplane1.id,))
        response = self.client.get(url)
        serializer = AirplaneRetrieveSerializer(self.airplane1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_airplane_forbidden(self):
        payload = {
            "name": "Airplane 3",
            "airplane_type": self.type_1,
            "rows": 12,
            "seats_in_row": 8
        }
        response = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com", password="1qazcde3", is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_airplane_admin(self):
        airplane_type = AirplaneType.objects.create(name="Type 1")
        payload = {
            "name": "Airplane 3",
            "airplane_type": airplane_type.id,
            "rows": 44,
            "seats_in_row": 10,
        }
        response = self.client.post(AIRPLANE_URL, payload)
        airplane = Airplane.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload.keys():
            if key == "airplane_type":
                self.assertEqual(payload[key], airplane.airplane_type.id)
            else:
                self.assertEqual(payload[key], getattr(airplane, key))
