"""
Tests for payment API.
"""

from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

from rest_framework.test import APIClient
from rest_framework import status
from core.models import Category,Product,Cart,DiscountCoupon,Payment,PaymentProduct,Address,DeliveryAddress
from core.tasks import send_email
from unittest import mock
import requests

PAYMENT_URL = reverse("payment:payment-list")
VALIDATION_URL = reverse("payment:validate")
DOWNLOAD_URL = reverse("payment:download")

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

def create_cart(**params):
    """Create and return a new product to cart."""
    return Cart.objects.create(**params)

def create_coupon(**params):
    """Create and return a new discount_coupon."""
    return DiscountCoupon.objects.create(**params)

def create_payment(**params):
    """Create and return a new payment object."""
    return Payment.objects.create(**params)

def create_payment_product(**params):
    """Create and return a new payment product object."""
    return PaymentProduct.objects.create(**params)

def create_address(**params):
    """Create and return new address"""
    return Address.objects.create(**params)

def create_delivery_address(**params):
    """Create and return a new delivery address"""
    return DeliveryAddress.objects.create(**params)

class PrivatePaymentApiTests(TestCase):
    """Unit test for payment api."""

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
    
    def test_create_payment_api_unavailable(self):
        """Test create payment when Khalti is down"""
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
        url = PAYMENT_URL
        data = {} 

        with mock.patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException()

            response = self.client.post(url, data)
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertEqual(response.data['detail'], 'Service Unavailable.')

    @mock.patch('payment.views.uuid.uuid4') 
    @mock.patch('payment.views.generate_unique_id')
    def test_create_payment_api_bad_request(self,mock_generate_id, mock_uuid):
        """Test create payment with invalid data."""

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
        mock_uuid.return_value = '190888e6-64cd-4dd1-a8fe-80fac3e1c7da' 
        mock_generate_id.return_value = '190888e6-64cd-4dd1-a8fe-80fac3e1c7da' 
        url = PAYMENT_URL
        data = {} 
        api_data = {'purchase_order_id': '190888e6-64cd-4dd1-a8fe-80fac3e1c7da', 
                    'purchase_order_name': '190888e6-64cd-4dd1-a8fe-80fac3e1c7da', 
                    'amount': 0, 
                    'return_url': 'http://testserver/api/payment/validate/', 
                    'website_url': 'http://testserver/', 
                    'product_details': []
                }
        mock_response = mock.MagicMock()
        mock_response.status_code = status.HTTP_400_BAD_REQUEST
        mock_response.json.return_value = {
            "return_url": [
                "Enter a valid URL."
            ],
            "website_url": [
                "Enter a valid URL."
            ],
            "amount": [
                "Amount should be greater than Rs. 1 that is 100 paisa."
            ],
            "error_key": "validation_error"
        }

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value = mock_response

            response = self.client.post(url, json=data)
            # Assertions
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json(), {
                "return_url": [
                    "Enter a valid URL."
                ],
                "website_url": [
                    "Enter a valid URL."
                ],
                "amount": [
                    "Amount should be greater than Rs. 1 that is 100 paisa."
                ],
                "error_key": "validation_error"
            })
            
            mock_post.assert_called_with(
                url=settings.PAYMENT_URL, 
                json=api_data,
                headers={"Authorization":settings.KHALTI_API_KEY}
            )

    @mock.patch('payment.views.uuid.uuid4') 
    @mock.patch('payment.views.generate_unique_id')
    def test_create_payment_api_success(self,mock_generate_id, mock_uuid):
        """Test create payment with empty cart"""

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
        mock_uuid.return_value = '190888e6-64cd-4dd1-a8fe-80fac3e1c7da' 
        mock_generate_id.return_value = '190888e6-64cd-4dd1-a8fe-80fac3e1c7da' 
        url = PAYMENT_URL
        data = {} 
        api_data = {'purchase_order_id': '190888e6-64cd-4dd1-a8fe-80fac3e1c7da',
                    'purchase_order_name': '190888e6-64cd-4dd1-a8fe-80fac3e1c7da',
                    'amount': 0,
                    'return_url': 'http://testserver/api/payment/validate/', 
                    'website_url': 'http://testserver/', 
                    'product_details': []
                }
        mock_response = mock.MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.json.return_value = {
            "pidx": "Vf735uANUTUUKtmfjSSX5A",
            "payment_url": "https://test-pay.khalti.com/?pidx=Vf735uANUTUUKtmfjSSX5A",
            "expires_at": "2023-09-22T09:01:05.627170+05:45",
            "expires_in": 1800,
            'message': 'Success',
        }

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value = mock_response

            response = self.client.post(url, json=data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.json(), {
                "pidx": "Vf735uANUTUUKtmfjSSX5A",
                "payment_url": "https://test-pay.khalti.com/?pidx=Vf735uANUTUUKtmfjSSX5A",
                "expires_at": "2023-09-22T09:01:05.627170+05:45",
                "expires_in": 1800,
                'message': 'Success',
            })
            
            mock_post.assert_called_with(
                url=settings.PAYMENT_URL, 
                json=api_data,
                headers={"Authorization":settings.KHALTI_API_KEY}
            )

    @mock.patch('payment.views.uuid.uuid4') 
    @mock.patch('payment.views.generate_unique_id')
    def test_create_payment_api_success_with_items(self,mock_generate_id, mock_uuid):
        """Test payment without coupon_code."""
        procuct = {
            "name": "Macbook Pro M1 Pro",
            "price": 265000,
            "stock":10,
            "threshold":2
        }
        p1 = create_product(**procuct)

        procuct = {
            "name": "Macbook Pro M2 Pro",
            "price": 275000,
            "stock":10,
            "threshold":2
        }
        p2 = create_product(**procuct)

        procuct = {
            "name": "Macbook Pro M1 MAX",
            "price": 215000,
            "stock":10,
            "threshold":2
        }
        p3 = create_product(**procuct)

        cart = {
            "p_id":p1,
            "quantity":2,
            "user":self.user
        }
        create_cart(**cart)

        cart = {
            "p_id":p2,
            "quantity":2,
            "user":self.user
        }
        create_cart(**cart)

        cart = {
            "p_id":p3,
            "quantity":2,
            "user":self.user
        }
        create_cart(**cart)

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

        mock_uuid.return_value = '190888e6-64cd-4dd1-a8fe-80fac3e1c7da' 
        mock_generate_id.return_value = '190888e6-64cd-4dd1-a8fe-80fac3e1c7da' 
        url = PAYMENT_URL
        data = {} 
        api_data = {
            "purchase_order_id": "190888e6-64cd-4dd1-a8fe-80fac3e1c7da",
            "purchase_order_name": "190888e6-64cd-4dd1-a8fe-80fac3e1c7da",
            "amount": 151000000,
            "return_url": "http://testserver/api/payment/validate/",
            "website_url": "http://testserver/",
            "product_details": [
                {
                "name": "Macbook Pro M1 Pro",
                "unit_price": 265000,
                "quantity": 2,
                "total_price": 530000,
                "identity": f"{p1.p_id}",
                "id": p1.p_id
                },
                {
                "name": "Macbook Pro M2 Pro",
                "unit_price": 275000,
                "quantity": 2,
                "total_price": 550000,
                "identity": f"{p2.p_id}",
                "id": p2.p_id
                },
                {
                "name": "Macbook Pro M1 MAX",
                "unit_price": 215000,
                "quantity": 2,
                "total_price": 430000,
                "identity": f"{p3.p_id}",
                "id": p3.p_id
                }
            ]
            }
        mock_response = mock.MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.json.return_value = {
            "pidx": "Vf735uANUTUUKtmfjSSX5A",
            "payment_url": "https://test-pay.khalti.com/?pidx=Vf735uANUTUUKtmfjSSX5A",
            "expires_at": "2023-09-22T09:01:05.627170+05:45",
            "expires_in": 1800,
            'message': 'Success',
        }

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value = mock_response

            response = self.client.post(url, json=data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.json(), {
                "pidx": "Vf735uANUTUUKtmfjSSX5A",
                "payment_url": "https://test-pay.khalti.com/?pidx=Vf735uANUTUUKtmfjSSX5A",
                "expires_at": "2023-09-22T09:01:05.627170+05:45",
                "expires_in": 1800,
                'message': 'Success',
            })
            
            mock_post.assert_called_with(
                url=settings.PAYMENT_URL, 
                json=api_data,
                headers={"Authorization":settings.KHALTI_API_KEY}
            )

    @mock.patch('payment.views.uuid.uuid4') 
    @mock.patch('payment.views.generate_unique_id')
    def test_create_payment_api_success_with_items_and_coupon_code(self,mock_generate_id, mock_uuid):
        """Test make payment with coupon_code"""
        coupon = {
            "user":self.user,
            "coupon_code":"abc123",
            "max_amount":100,
            "max_percentage":2,
            "used":False
            }
        create_coupon(**coupon)

        coupon2 = {
            "user":self.user,
            "coupon_code":"abc113",
            "max_amount":10000000,
            "max_percentage":2,
            "used":False
            }
        create_coupon(**coupon2)

        procuct = {
            "name": "Macbook Pro M1 Pro",
            "price": 265000,
            "stock":10,
            "threshold":2
        }
        p1 = create_product(**procuct)

        procuct = {
            "name": "Macbook Pro M2 Pro",
            "price": 275000,
            "stock":10,
            "threshold":2
        }
        p2 = create_product(**procuct)

        procuct = {
            "name": "Macbook Pro M1 MAX",
            "price": 215000,
            "stock":10,
            "threshold":2
        }
        p3 = create_product(**procuct)

        cart = {
            "p_id":p1,
            "quantity":2,
            "user":self.user
        }
        create_cart(**cart)

        cart = {
            "p_id":p2,
            "quantity":2,
            "user":self.user
        }
        create_cart(**cart)

        cart = {
            "p_id":p3,
            "quantity":2,
            "user":self.user
        }
        create_cart(**cart)
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
        mock_uuid.return_value = '190888e6-64cd-4dd1-a8fe-80fac3e1c7da' 
        mock_generate_id.return_value = '190888e6-64cd-4dd1-a8fe-80fac3e1c7da' 
        url = PAYMENT_URL
        api_data = {
            "purchase_order_id": "190888e6-64cd-4dd1-a8fe-80fac3e1c7da",
            "purchase_order_name": "190888e6-64cd-4dd1-a8fe-80fac3e1c7da",
            "amount": 150990000,
            "return_url": "http://testserver/api/payment/validate/",
            "website_url": "http://testserver/",
            "product_details": [
                {
                "name": "Macbook Pro M1 Pro",
                "unit_price": 265000,
                "quantity": 2,
                "total_price": 530000,
                "identity": f"{p1.p_id}",
                "id": p1.p_id
                },
                {
                "name": "Macbook Pro M2 Pro",
                "unit_price": 275000,
                "quantity": 2,
                "total_price": 550000,
                "identity": f"{p2.p_id}",
                "id": p2.p_id
                },
                {
                "name": "Macbook Pro M1 MAX",
                "unit_price": 215000,
                "quantity": 2,
                "total_price": 430000,
                "identity": f"{p3.p_id}",
                "id": p3.p_id
                }
            ]
            }
        mock_response = mock.MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.json.return_value = {
            "pidx": "Vf735uANUTUUKtmfjSSX5A",
            "payment_url": "https://test-pay.khalti.com/?pidx=Vf735uANUTUUKtmfjSSX5A",
            "expires_at": "2023-09-22T09:01:05.627170+05:45",
            "expires_in": 1800,
            'message': 'Success',
        }
        data = {"coupon_code":coupon["coupon_code"]} 
        with mock.patch('requests.post') as mock_post:
            mock_post.return_value = mock_response

            response = self.client.post(url, data=data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.json(), {
                "pidx": "Vf735uANUTUUKtmfjSSX5A",
                "payment_url": "https://test-pay.khalti.com/?pidx=Vf735uANUTUUKtmfjSSX5A",
                "expires_at": "2023-09-22T09:01:05.627170+05:45",
                "expires_in": 1800,
                'message': 'Success',
            })
            
            mock_post.assert_called_with(
                url=settings.PAYMENT_URL, 
                json=api_data,
                headers={"Authorization":settings.KHALTI_API_KEY}
            )
        
        mock_response = mock.MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.json.return_value = {
            "pidx": "Va735uANUTUUKtmfjSSX5A",
            "payment_url": "https://test-pay.khalti.com/?pidx=Vf735uANUTUUKtmfjSSX5A",
            "expires_at": "2023-09-22T09:01:05.627170+05:45",
            "expires_in": 1800,
            'message': 'Success',
        }
        data = {"coupon_code":coupon2["coupon_code"]} 
        api_data = {
            "purchase_order_id": "190888e6-64cd-4dd1-a8fe-80fac3e1c7da",
            "purchase_order_name": "190888e6-64cd-4dd1-a8fe-80fac3e1c7da",
            "amount": 147980000,
            "return_url": "http://testserver/api/payment/validate/",
            "website_url": "http://testserver/",
            "product_details": [
                {
                "name": "Macbook Pro M1 Pro",
                "unit_price": 265000,
                "quantity": 2,
                "total_price": 530000,
                "identity": f"{p1.p_id}",
                "id": p1.p_id
                },
                {
                "name": "Macbook Pro M2 Pro",
                "unit_price": 275000,
                "quantity": 2,
                "total_price": 550000,
                "identity": f"{p2.p_id}",
                "id": p2.p_id
                },
                {
                "name": "Macbook Pro M1 MAX",
                "unit_price": 215000,
                "quantity": 2,
                "total_price": 430000,
                "identity": f"{p3.p_id}",
                "id": p3.p_id
                }
            ]
            }
        with mock.patch('requests.post') as mock_post:
            mock_post.return_value = mock_response

            response = self.client.post(url, data=data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.json(), {
                "pidx": "Va735uANUTUUKtmfjSSX5A",
                "payment_url": "https://test-pay.khalti.com/?pidx=Vf735uANUTUUKtmfjSSX5A",
                "expires_at": "2023-09-22T09:01:05.627170+05:45",
                "expires_in": 1800,
                'message': 'Success',
            })
            
            mock_post.assert_called_with(
                url=settings.PAYMENT_URL, 
                json=api_data,
                headers={"Authorization":settings.KHALTI_API_KEY}
            )

    def test_get_payment_list_success(self):
        """Test Get list of payment made by user"""
        payment = {
            "id":"xyz",
            "quantity":5,
            "status":"Completed",
            "transaction_id":"xyz",
            "amount":1000,
            "user":self.user,
        }
        create_payment(**payment)
        response = self.client.get(PAYMENT_URL)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()["results"]),1)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True,CELERY_TASK_EAGER_PROPOGATES=True)
    def test_validate_payment_success(self):
        """Validate user payment."""
        procuct = {
            "name": "Macbook Pro M1 Pro",
            "price": 265000,
            "stock":10,
            "threshold":2
        }
        p1 = create_product(**procuct)

        procuct = {
            "name": "Macbook Pro M2 Pro",
            "price": 275000,
            "stock":10,
            "threshold":2
        }
        p2 = create_product(**procuct)

        procuct = {
            "name": "Macbook Pro M1 MAX",
            "price": 215000,
            "stock":10,
            "threshold":2
        }
        p3 = create_product(**procuct)
        payment = {
            "id":"xyz",
            "quantity":5,
            "status":"Pending",
            'date_time': '2023-09-22T06:05:29.227784Z', 
            "amount":1000,
            "user":self.user,
        }
        p = create_payment(**payment)
        payment_product = {
            "payment_id":p,
            "product":p1,
            "quantity":10,
            "amount":123
        }
        create_payment_product(**payment_product)
        payment_product = {
            "payment_id":p,
            "product":p2,
            "quantity":1,
            "amount":123
        }
        create_payment_product(**payment_product)
        payment_product = {
            "payment_id":p,
            "product":p3,
            "quantity":1,
            "amount":123
        }
        create_payment_product(**payment_product)

        mock_response = mock.MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.json.return_value = {
            "pidx": "xyz",
            "total_amount": 2000,
            "status": "Completed",
            "transaction_id": "xyz",
            "fee": 0,
            "refunded": False
        }
        with mock.patch('requests.post') as mock_get:
            mock_get.return_value.status_code = status.HTTP_200_OK
            mock_get.return_value = mock_response
            with mock.patch('payment.views.send_email') as mock_send_email:
                response = self.client.get(VALIDATION_URL+"?pidx=xyz&transaction_id=xyz&amount=1000")
                self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_validate_payment_not_found(self):
        """Validate user payment."""
        payment = {
            "id":"xyz",
            "quantity":5,
            "status":"Completed",
            "transaction_id":"xyz",
            'date_time': '2023-09-22T06:05:29.227784Z', 
            "amount":1000,
            "user":self.user,
        }
        create_payment(**payment)

        mock_response = mock.MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.json.return_value = {
            "pidx": "xyz",
            "total_amount": 2000,
            "status": "Completed",
            "transaction_id": "xyz",
            "fee": 0,
            "refunded": False
        }
        with mock.patch('requests.get') as mock_get:
            mock_get.return_value = mock_response
            response = self.client.get(VALIDATION_URL+"?pidx=xyz1&transaction_id=xyz&amount=1000")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json(),{'error': 'Payment not found'})
    
    @mock.patch('requests.post')  
    def test_validate_payment_service_unavailable(self,mock_get):
        payment = {
            "id":"xyz",
            "quantity":5,
            "status":"Pending",
            'date_time': '2023-09-22T06:05:29.227784Z', 
            "amount":1000,
            "user":self.user,
        }
        create_payment(**payment)
        
        mock_get.side_effect = requests.exceptions.RequestException()

        response = self.client.get(VALIDATION_URL+"?pidx=xyz&transaction_id=xyz&amount=1000")
        # mock_exception.assert_called()  
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_validate_status_not_completed(self):
        """Test validate with payment status not completed"""
        payment = {
            "id":"xyz",
            "quantity":5,
            "status":"Pending",
            'date_time': '2023-09-22T06:05:29.227784Z', 
            "amount":1000,
            "user":self.user,
        }
        create_payment(**payment)

        mock_response = mock.MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.json.return_value = {
            "pidx": "xyz",
            "total_amount": 2000,
            "status": "Pending",
            "fee": 0,
            "refunded": False
        }
        with mock.patch('payment.views.requests.post') as mock_get:
            mock_get.return_value = mock_response
            response = self.client.get(VALIDATION_URL+"?pidx=xyz&transaction_id=xyz&amount=1000")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json(),{'error': 'Payment Not Completed'})

    def test_validate_response_not_200(self):
        """Test validate with payment status not completed"""
        payment = {
            "id":"xyz",
            "quantity":5,
            "status":"Pending",
            'date_time': '2023-09-22T06:05:29.227784Z', 
            "amount":1000,
            "user":self.user,
        }
        create_payment(**payment)

        mock_response = mock.MagicMock()
        mock_response.status_code = status.HTTP_400_BAD_REQUEST
        mock_response.json.return_value = {
            "pidx": "xyz",
            "total_amount": 2000,
            "status": "Pending",
            "fee": 0,
            "refunded": False
        }
        with mock.patch('payment.views.requests.post') as mock_get:
            mock_get.return_value = mock_response
            response = self.client.get(VALIDATION_URL+"?pidx=xyz&transaction_id=xyz&amount=1000")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json(),{'error': 'Bad Request'})

    def test_validate_bad_request(self):
        """Test validate with payment status not completed"""
        payment = {
            "id":"xyz",
            "quantity":5,
            "status":"Pending",
            'date_time': '2023-09-22T06:05:29.227784Z', 
            "amount":1000,
            "user":self.user,
        }
        create_payment(**payment)

        mock_response = mock.MagicMock()
        mock_response.status_code = status.HTTP_400_BAD_REQUEST
        mock_response.json.return_value = {
            "pidx": "xyz",
            "total_amount": 2000,
            "status": "Pending",
            "fee": 0,
            "refunded": False
        }
        with mock.patch('payment.views.requests.post') as mock_get:
            mock_get.return_value = mock_response
            response = self.client.get(VALIDATION_URL+"?pidx=xyz&amount=1000")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json(),{'error': 'Invalid Request'})

    def test_download_file_not_found(self):
        """Test downloading file when payment doesnot exist."""
        response = self.client.get(DOWNLOAD_URL+"?id=12345")

        self.assertIn("detail",response.json().keys())
        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)

    @mock.patch('payment.views.open', side_effect=IOError("Mocked file open error"))
    def test_download_file_reading_error(self,os_path_exists):
        """Test downloading file when payment doesnot exist."""
        payment = {
            "id":"xyz",
            "quantity":5,
            "status":"Completed",
            'date_time': '2023-09-22T06:05:29.227784Z', 
            "amount":1000,
            "user":self.user,
        }
        create_payment(**payment)
        response = self.client.get(DOWNLOAD_URL+"?id=xyz")

        self.assertIn("error",response.json().keys())
        self.assertEqual(response.status_code,status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_download_file_success(self):
        """Test downloading file for user's payment."""
        payment = {
            "id":"xyz",
            "quantity":5,
            "status":"Completed",
            'date_time': '2023-09-22T06:05:29.227784Z', 
            "amount":1000,
            "user":self.user,
        }
        create_payment(**payment)
        response = self.client.get(DOWNLOAD_URL+"?id=xyz")
        self.assertEqual(response.status_code,status.HTTP_200_OK)
