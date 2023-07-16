"""
Tests for product API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Product,Review,Category
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

PRODUCT_URL = reverse('product:product-list')
PRODUCT_DETAIL_URL = reverse('product:product-detail', args=[1])

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

def create_product(**params):
    """Create and return a new product"""
    category = Category(category="Electornics")
    category.save()
    category = Category.objects.get(category="Electornics")
    params["category"] = category
    product = Product.objects.create(**params)
    return product

class PublicUserApiTests(TestCase):
    """Test the public features of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_get_products_success(self):
        """Test get products"""
        procuct = {
            "name": "Macbook Pro M1 Pro",
            "price": 265000,
            "stock":10,
            "threshold":2
        }
        create_product(**procuct)
        res = self.client.get(PRODUCT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('name',res.data["results"][0])

    def test_get_product_detail_success(self):
        """Test get products"""
        product = {
            "name": "Macbook Pro M1 Pro",
            "price": 265000,
            "stock":10,
            "threshold":2
        }
        user = {
            "first_name" : "xyz",
            "last_name" : "abc",
            "phone" : "1234",
            "email" : "user@example.com",
            "password" : "test123"
        }
        product = create_product(**product)
        product = Product.objects.get(p_id=1)
        review = Review(p_id=product,review="Good",rating=5,user=create_user(**user))
        review.save()
        res = self.client.get(PRODUCT_DETAIL_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('name',res.data.keys())