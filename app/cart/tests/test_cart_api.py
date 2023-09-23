"""
Tests for cart API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Cart,Product,Category
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CART_LIST = reverse('cart:cart-list')
CART_DETAIL = reverse('cart:cart-detail',args=[1])

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

def create_cart(**params):
    """Create and return a new product to cart."""
    return Cart.objects.create(**params)

class PrivateCartAPITest(TestCase):
    """Test cases for cart API."""

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
    
    def test_create_cart_success(self):
        """Test create cart successful."""

        procuct = {
            "name": "Macbook Pro M1 Pro",
            "price": 265000,
            "stock":10,
            "threshold":2
        }
        p = create_product(**procuct)
        data = {
            'p_id':p.p_id,
            'quantity':3,
            'user':self.user
        }
        response = self.client.post(CART_LIST,data=data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertIn('id',response.json().keys())

    def test_create_cart_invalid_product(self):
        """Test creating cart with invalid p_id"""
        data = {
            'p_id':1,
            'quantity':3,
            'user':self.user
        }
        response = self.client.post(CART_LIST,data=data)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn('p_id',response.json().keys())
    
    def test_update_cart_success(self):
        """Test updating cart with quantity within stock"""
        procuct = {
            "name": "Macbook Pro M1 Pro",
            "price": 265000,
            "stock":10,
            "threshold":2
        }
        p = create_product(**procuct)
        data = {
            'p_id':p.p_id,
            'quantity':2,
            'user':self.user
        }
        response = self.client.post(CART_LIST,data=data)
        response = self.client.post(CART_LIST,data=data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertIn('p_id',response.json().keys())

    def test_create_cart_stock_exceeded(self):
        """Test creating cart with quantity more than stock"""
        procuct = {
            "name": "Macbook Pro M1 Pro",
            "price": 265000,
            "stock":10,
            "threshold":2
        }
        p = create_product(**procuct)
        data = {
            'p_id':p.p_id,
            'quantity':15,
            'user':self.user
        }
        response = self.client.post(CART_LIST,data=data)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn('error',response.json().keys())

    def test_update_cart_stock_exceeded(self):
        """Test updating cart with quantity more than stock"""
        procuct = {
            "name": "Macbook Pro M1 Pro",
            "price": 265000,
            "stock":10,
            "threshold":2
        }
        p = create_product(**procuct)
        data = {
            'p_id':p.p_id,
            'quantity':7,
            'user':self.user
        }
        response = self.client.post(CART_LIST,data=data)
        response = self.client.post(CART_LIST,data=data)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn('error',response.json().keys())

    def test_get_cart_list_success(self):
        """Test getting list of items in cart"""
        procuct = {
            "name": "Macbook Pro M1 Pro",
            "price": 265000,
            "stock":10,
            "threshold":2
        }
        p = create_product(**procuct)
        data = {
            'p_id':p,
            'quantity':3,
            'user':self.user
        }
        create_cart(**data)
        response = self.client.get(CART_LIST)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]),1)