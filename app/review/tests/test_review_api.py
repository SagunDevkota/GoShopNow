"""
Tests for product review api.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Review,Product,Category
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

REVIEW_LIST = reverse("review:review-list")
REVIEW_OBJECT = reverse("review:review-detail", args=[1])

def create_review(**params):
    """Create review for a product."""
    return Review.objects.create(**params)

def create_product(**params):
    """Create and return a new product"""
    category = Category(category="Electornics")
    category.save()
    category = Category.objects.get(category="Electornics")
    params["category"] = category
    product = Product.objects.create(**params)
    return product

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
        self.user = create_user(**user)
        self.client.force_authenticate(self.user)
        product = {
            "name": "Macbook Pro M1 Pro",
            "price": 265000,
            "stock":10,
            "threshold":2
        }
        self.product = create_product(**product)
    
    def test_create_review_success(self):
        """Test creating review for a valid product."""
        
        review = {
            "p_id": self.product.p_id,  # Use "p_id" as the key
            "review": "good",
            "rating": 5,
        }
        res = self.client.post(REVIEW_LIST, review)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)

    def test_create_review_invalid_product(self):
        """Throw error if product doesnot exists."""
        review = {
            "p_id": 0,  # Use "p_id" as the key
            "review": "good",
            "rating": 5,
        }
        res = self.client.post(REVIEW_LIST, review)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn("p_id",res.json().keys())

    def test_invalid_rating(self):
        """Throw error if rating is invalid."""
        review = {
            "p_id": self.product.p_id,  # Use "p_id" as the key
            "review": "good",
            "rating": 6,
        }
        res = self.client.post(REVIEW_LIST, review)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating",res.json().keys())

        review = {
            "p_id": self.product.p_id,  # Use "p_id" as the key
            "review": "good",
            "rating": 0,
        }
        res = self.client.post(REVIEW_LIST, review)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating",res.json().keys())

    def test_wrong_user_added(self):
        """Ignore the user parameter of the request"""
        review = {
            "p_id": self.product.p_id,  # Use "p_id" as the key
            "review": "good",
            "rating": 4,
            "user":1,
        }
        res = self.client.post(REVIEW_LIST, review)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)


    def test_get_review_list_success(self):
        """Test get review list."""
        pass