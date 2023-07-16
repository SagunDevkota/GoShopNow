"""
Tests for product review api.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Review,Product,Category,Payment
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


REVIEW_LIST = reverse("review:review-list")
REVIEW_OBJECT = reverse("review:review-detail",args=[1])

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

def create_payment(**params):
    """create and return a new payment object."""
    return Payment.objects.create(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API"""
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

    def test_get_review_list_without_id(self):
        """Raise error if id not provided in list endpoint"""
        res = self.client.get(REVIEW_LIST)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn("error",res.json().keys())

    def test_get_review_list_success(self):
        """Raise error if id not provided in list endpoint"""
        review = {
            "p_id": self.product.p_id,  # Use "p_id" as the key
            "review": "good",
            "rating": 5,
        }
        payment = {
            "id":"123",
            "quantity":"1",
            "status":"Completed",
            "transaction_id":"transaction",
            "amount":123,
            "user":self.user,
            "product":self.product
        }
        create_payment(**payment)
        res = self.client.post(REVIEW_LIST, review)
        res = self.client.get(REVIEW_LIST+"?p_id="+str(res.json()["p_id"]))
        self.assertEqual(res.status_code,status.HTTP_200_OK)

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

        product = {
            "name": "Macbook Pro M2 Pro",
            "price": 265000,
            "stock":10,
            "threshold":2
        }
        product = create_product(**product)
        review = {
            "p_id": product,  # Use "p_id" as the key
            "review": "good",
            "rating": 5,
            "user":self.user
        }
        payment = {
            "id":"1234",
            "quantity":"1",
            "status":"Completed",
            "transaction_id":"transaction",
            "amount":123,
            "user":self.user,
            "product":product
        }
        create_payment(**payment)
        self.review = create_review(**review)
    
    def test_create_review_success(self):
        """Test creating review for a valid product."""
        
        review = {
            "p_id": self.product.p_id,  # Use "p_id" as the key
            "review": "good",
            "rating": 5,
        }
        payment = {
            "id":"123",
            "quantity":"1",
            "status":"Completed",
            "transaction_id":"transaction",
            "amount":123,
            "user":self.user,
            "product":self.product
        }
        create_payment(**payment)
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
        payment = {
            "id":"123",
            "quantity":"1",
            "status":"Completed",
            "transaction_id":"transaction",
            "amount":123,
            "user":self.user,
            "product":self.product
        }
        create_payment(**payment)
        res = self.client.post(REVIEW_LIST, review)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)

    def test_create_review_without_purchase(self):
        """Raise error if review is attempted before purchase."""
        review = {
            "p_id": self.product.p_id,  # Use "p_id" as the key
            "review": "good",
            "rating": 4,
            "user":1,
        }
        res = self.client.post(REVIEW_LIST, review)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_multiple_review_from_one_user(self):
        """Raise error if one user attempts to post multiple review for a product."""
        review = {
            "p_id": self.product.p_id,  # Use "p_id" as the key
            "review": "good",
            "rating": 4,
            "user":1,
        }
        payment = {
            "id":"123",
            "quantity":"1",
            "status":"Completed",
            "transaction_id":"transaction",
            "amount":123,
            "user":self.user,
            "product":self.product
        }
        create_payment(**payment)
        res = self.client.post(REVIEW_LIST, review)
        res = self.client.post(REVIEW_LIST, review)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn("error",res.json().keys())

    def test_create_review_without_payment_cleared(self):
        """Raise error if payment is not cleared"""
        product = {
            "name": "Macbook Pro M1 Pro",
            "price": 265000,
            "stock":10,
            "threshold":2
        }
        product = create_product(**product)
        review = {
            "p_id": product.p_id,  # Use "p_id" as the key
            "review": "good",
            "rating": 5,
            "user":self.user
        }
        payment = {
            "id":"12345",
            "quantity":"1",
            "status":"Pending",
            "transaction_id":"transaction",
            "amount":123,
            "user":self.user,
            "product":product
        }
        create_payment(**payment)
        res = self.client.post(REVIEW_LIST,review)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn("error",res.json())


    def test_delete_review_of_another_user(self):
        """Raise error if one user attempts to delete review of another user."""
        user = {
            "first_name" : "xyz",
            "last_name" : "abc",
            "phone" : "1234",
            "email" : "user1@example.com",
            "password" : "test123"
        }
        self.user = create_user(**user)
        self.client.force_authenticate(self.user)
        REVIEW_OBJECT = reverse("review:review-detail",args=[self.review.id])
        res = self.client.delete(REVIEW_OBJECT)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn("error",res.json().keys())

    def test_delete_review_by_same_user(self):
        """Succes if same user tries to delete their review."""
        REVIEW_OBJECT = reverse("review:review-detail",args=[self.review.id])
        res = self.client.delete(REVIEW_OBJECT)
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)

    def test_delete_review_doesnot_exist(self):
        """Raise error if user tries to delete non-existant review"""
        REVIEW_OBJECT = reverse("review:review-detail",args=[1234])
        res = self.client.delete(REVIEW_OBJECT)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn('error',res.json().keys())