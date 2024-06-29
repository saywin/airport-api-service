from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from flights.models import Route, Airport
from flights.serializers import RouteListSerializer


class BaseRouteAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.airport_1 = Airport.objects.create(
            name="Test Airport 1",
            closest_big_city="Test City 1"
        )
        self.airport_2 = Airport.objects.create(
            name="Test Airport 2",
            closest_big_city="Test City 2"
        )
        self.airport_3 = Airport.objects.create(
            name="Test Airport 3",
            closest_big_city="Test City 3"
        )
        self.route = Route.objects.create(
            distance=1000,
            source=self.airport_1,
            destination=self.airport_2
        )
        self.route_2 = Route.objects.create(
            distance=1500,
            source=self.airport_2,
            destination=self.airport_3
        )
        self.payload = {
            "distance": 1000,
            "source": self.airport_2.id,
            "destination": self.airport_1.id,
        }
        self.route_list_url = reverse("flights:route-list")
        self.route_detail_url = reverse(
            "flights:route-detail", args=[self.route.id]
        )


class UnAuthenticatedRouteApiTest(BaseRouteAPITest):
    def test_get_flight_list_unauthorized(self):
        response = self.client.get(self.route_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_flight_detail_unauthorized(self):
        detail_url = self.route_detail_url
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTest(BaseRouteAPITest):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            email="user@user.com", password="1qazcde3"
        )
        self.client.force_authenticate(user=self.user)

    def test_auth_required_user(self):
        response = self.client.get(self.route_list_url)
        route = Route.objects.all().select_related()
        serializer = RouteListSerializer(route, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_route_detail_authenticated(self):
        response = self.client.get(self.route_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_route_filter_by_source(self):
        response = self.client.get(
            self.route_list_url, {"source": self.airport_1.id}
        )
        route = Route.objects.filter(source=self.airport_1)
        serializer = RouteListSerializer(route, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_route_filter_by_destination(self):
        response = self.client.get(
            self.route_list_url, {"destination": self.airport_2.id}
        )
        route = Route.objects.filter(destination=self.airport_2)
        serializer = RouteListSerializer(route, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_create_flight_forbidden(self):
        response = self.client.post(self.route_list_url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteAPITest(BaseRouteAPITest):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="1qazcde3",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_route_admin(self):
        response = self.client.post(self.route_list_url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_route_admin(self):
        response = self.client.delete(self.route_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
