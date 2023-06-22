"""
Tests for product review api.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Product,Review,Category
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

REVIEW_LIST = reverse("product:review-list")
REVIEW_OBJECT = reverse("product:review-detail", args=[1])
REVIEW_CREATE = reverse("product:review-create")

def create_review(**params):
    """Create review for a product."""
    return Review.objects.all(**params)

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

class PrivateRviewAPITests(TestCase):
    """Test cases for review api."""
    def setUp(self):
        self.client = APIClient()
        user = {
            "first_name" : "xyz",
            "last_name" : "abc",
            "phone" : "1234",
            "email" : "user@example.com",
            "password" : "test123"
        }
        user = create_user(**user)
        self.client.force_authenticate(user)
    
    def test_create_review_success(self):
        """Test creating review for a valid product."""
        review = {
            "p_id":1,
            "review":"good",
            "rating":5
        }

        res = self.client.post(REVIEW_CREATE,review)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)

    def test_get_review_list_success(self):
        """Test get review list."""
        pass