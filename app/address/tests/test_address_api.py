"""
Tests for cart API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import DeliveryAddress,Address
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

ADDRESS_GET = reverse("address:address-list")
USER_ADDRESS_GET = reverse("address:deliveryaddress-list")

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

def create_address(**params):
    """Create and return new address"""
    return Address.objects.create(**params)

def create_delivery_address(**params):
    """Create and return a new delivery address"""
    return DeliveryAddress.objects.create(**params)

class PrivateAddressAPI(TestCase):
    """"Testcases for address api."""
    def setUp(self) -> None:
        self.client = APIClient()
        payload = {
            "first_name" : "xyz",
            "last_name" : "abc",
            "phone" : "1234",
            "email" : "user@example.com",
            "password" : "test123"
        }
        self.user = create_user(**payload)
        self.client.force_authenticate(self.user)
        return super().setUp()
    
    def test_get_delivery_address_list_success(self):
        """Test get address list."""
        address = {
            "id":"1",
            "name":"xyz",
            "parent":None
        }
        a1 = create_address(**address)

        address = {
            "id":"2",
            "name":"xyz2",
            "parent":a1
        }
        a2 = create_address(**address)

        address = {
            "id":"3",
            "name":"xyz3",
            "parent":a2
        }
        a3 = create_address(**address)

        response = self.client.get(ADDRESS_GET)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_create_delivery_address_success(self):
        """Test create delivery address."""
        address = {
            "id":"1",
            "name":"xyz",
            "parent":None
        }
        a1 = create_address(**address)

        address = {
            "id":"2",
            "name":"xyz2",
            "parent":a1
        }
        a2 = create_address(**address)

        address = {
            "id":"3",
            "name":"xyz3",
            "parent":a2
        }
        a3 = create_address(**address)

        data = {
            "provience":a1.id,
            "city":a2.id,
            'area':a3.id
        }
        response = self.client.post(USER_ADDRESS_GET,data=data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)

    def test_update_delivery_address_success(self):
        """Test update delivery address."""
        address = {
            "id":"1",
            "name":"xyz",
            "parent":None
        }
        a1 = create_address(**address)

        address = {
            "id":"4",
            "name":"abc",
            "parent":None
        }
        a11 = create_address(**address)

        address = {
            "id":"2",
            "name":"xyz2",
            "parent":a1
        }
        a2 = create_address(**address)

        address = {
            "id":"3",
            "name":"xyz3",
            "parent":a2
        }
        a3 = create_address(**address)

        data = {
            "user":self.user,
            "provience":a1,
            "city":a2,
            'area':a3
        }
        create_delivery_address(**data)
        data = {
            "provience":a11.id,
            "city":a2.id,
            'area':a3.id
        }
        response = self.client.post(USER_ADDRESS_GET,data=data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)

    def test_get_user_address(self):
        """Test get user's delivery address"""
        address = {
            "id":"1",
            "name":"xyz",
            "parent":None
        }
        a1 = create_address(**address)
        
        address = {
            "id":"2",
            "name":"xyz2",
            "parent":a1
        }
        a2 = create_address(**address)

        address = {
            "id":"3",
            "name":"xyz3",
            "parent":a2
        }
        a3 = create_address(**address)

        data = {
            "user":self.user,
            "provience":a1,
            "city":a2,
            'area':a3
        }
        create_delivery_address(**data)

        response = self.client.get(USER_ADDRESS_GET)

        self.assertEqual(response.status_code,status.HTTP_200_OK)