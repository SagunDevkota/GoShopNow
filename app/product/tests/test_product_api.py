"""
Tests for product API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Product,Review,Category
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import Mock

from product.serializers import ProductSerializer

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
    
    def test_sort_by_price_success(self):
        """Test sort by price"""
        procuct = {
            "name": "Macbook Pro M1 Pro",
            "price": 265000,
            "stock":10,
            "threshold":2
        }
        create_product(**procuct)
        procuct = {
            "name": "Macbook Pro M2 Pro",
            "price": 275000,
            "stock":10,
            "threshold":2
        }
        create_product(**procuct)

        procuct = {
            "name": "Macbook Pro M1",
            "price": 215000,
            "stock":10,
            "threshold":2
        }
        create_product(**procuct)

        res = self.client.get(PRODUCT_URL+"?price=1")
        prices = []
        for product in res.json()['results']:
            prices.append(procuct["price"])
        sorted_prices = sorted(prices)
        self.assertEqual(sorted_prices,prices)

        res = self.client.get(PRODUCT_URL+"?price=-1")
        prices = []
        for product in res.json()['results']:
            prices.append(procuct["price"])
        sorted_prices = sorted(prices,reverse=True)
        self.assertEqual(sorted_prices[::-1],prices)

    def test_sort_by_rating_success(self):
        """Test sort by rating"""
        procuct = {
            "name": "Macbook Pro M1 Pro",
            "price": 265000,
            "stock":10,
            "threshold":2
        }
        p = create_product(**procuct)
        p.rating = 3
        p.save()
        procuct = {
            "name": "Macbook Pro M2 Pro",
            "price": 275000,
            "stock":10,
            "threshold":2
        }
        p = create_product(**procuct)
        p.rating = 4
        p.save()

        procuct = {
            "name": "Macbook Pro M1",
            "price": 215000,
            "stock":10,
            "threshold":2
        }
        p = create_product(**procuct)
        p.rating = 2
        res = self.client.get(PRODUCT_URL+"?rating=1")
        ratings = []
        for _ in res.json()['results']:
            ratings.append(_["rating"])
        sorted_ratings = sorted(ratings)
        self.assertEqual(sorted_ratings,ratings)

        res = self.client.get(PRODUCT_URL+"?rating=-1")
        ratings = []
        for _ in res.json()['results']:
            ratings.append(_["rating"])
        sorted_ratings = sorted(ratings,reverse=True)
        self.assertEqual(sorted_ratings[::-1],ratings)

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
        product = Product.objects.get(p_id=product.p_id)
        review = Review(p_id=product,review="Good",rating=5,user=create_user(**user))
        review.save()
        PRODUCT_DETAIL_URL = reverse('product:product-detail', args=[product.p_id])
        res = self.client.get(PRODUCT_DETAIL_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('name',res.data.keys())

    def test_returns_image_url_if_first_image_exists(self):
        product = Mock()
        first_image = Mock()
        first_image.image_url.url = "http://example.com/image.jpg"
        product.product_id_image.first.return_value = first_image

        serializer = ProductSerializer()
        result = serializer.get_image_url(product)

        self.assertEqual(result, "http://example.com/image.jpg")

    def test_returns_none_if_no_first_image(self):
        product = Mock()
        product.product_id_image.first.return_value = None

        serializer = ProductSerializer()
        result = serializer.get_image_url(product)

        self.assertIsNone(result)