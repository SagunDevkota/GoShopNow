"""
Tests for discount coupon API.
"""

from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

from rest_framework.test import APIClient
from rest_framework import status
from core.models import Category,Product,Cart,DiscountCoupon,Payment,PaymentProduct
from core.tasks import send_email
from unittest import mock
import requests
from discount.views import DiscountCouponViewSet
from discount.urls import router

DISCOUNT_URL = reverse("discount:discountcoupon-list")

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

def create_coupon(**params):
    """Create and return a new discount_coupon."""
    return DiscountCoupon.objects.create(**params)

class TestPrivateDiscountCouponAPI(TestCase):
    """"Unittest for discount coupon api."""

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
    
    def test_get_discount_coupon_success(self):
        """"Test list discount coupon of a user."""
        coupon = {
            "user":self.user,
            "coupon_code":"abc123",
            "max_amount":100,
            "max_percentage":2,
            "used":False
            }
        create_coupon(**coupon)

        response = self.client.get(DISCOUNT_URL)
        self.assertEqual(len(response.json()["results"]),1)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
