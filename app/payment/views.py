"""View for review model"""

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import BasePermission
from rest_framework import status
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from drf_spectacular.openapi import OpenApiParameter
from drf_spectacular.utils import extend_schema

from rest_framework_simplejwt.authentication import JWTAuthentication

from payment import serializers,exceptions

from core.models import Payment,Product,Cart,PaymentProduct,User
from core.pagination import CustomPagination

import requests

from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseForbidden
import uuid
import json

def generate_unique_id():
    return str(uuid.uuid4())

class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):        
        if view.action == 'validate':
            return True  # Allow all GET requests without authentication
        return request.user and request.user.is_authenticated  # Require authentication for other methods

class PaymentViewSet(viewsets.GenericViewSet,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin):
    """View for payment model."""
    serializer_class = serializers.PaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    queryset = Payment.objects.all()
    
    def get_serializer_class(self):
        if self.action == "create":
            return serializers.CreatePaymentSerializer
        else:
            return self.serializer_class
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-date_time")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        data = serializer.data
        product_details = []
        total_amount = 0
        print(data)
        if("product" in data.keys() and "quantity" in data.keys()):
            item = {}
            item["p_id_id"] = data["product"].p_id
            item["quantity"] = data["quantity"]
            items = [item]
        elif("product" in data.keys() or "quantity" in data.keys()):
            raise ValidationError({"error":["Invalid Request"]})
        else:
            items = list(Cart.objects.filter(user=self.request.user).values())

        print(items)
        product_details = []
        total_quantity = 0
        total_amount = 0
        for item in items:
            record = {}
            product = Product.objects.get(p_id=item["p_id_id"])
            record["name"] = product.name
            record["unit_price"] = product.price
            record["quantity"] = item['quantity']
            record["total_price"] = item["quantity"]*product.price
            record["identity"] = str(product.p_id)
            record['id'] = item["p_id_id"]
            product_details.append(record)
            total_amount += product.price*item["quantity"]
            total_quantity += item['quantity']

        purchase_id = generate_unique_id()
        payload = {
            "purchase_order_id":purchase_id,
            "purchase_order_name":purchase_id,
            "amount":total_amount*100, #convert to paisa
            "return_url": self.request.build_absolute_uri(reverse('payment:validate')),
            "website_url": self.request.build_absolute_uri("/"),
            "product_details":product_details
        }
        headers = {
            "Authorization" : settings.KHALTI_API_KEY
        }
        try:
            response = requests.post(url=settings.PAYMENT_URL, json=payload, headers=headers)
            response_data = response.json()
        except:
            raise exceptions.ServiceUnavailable()
        if response.status_code == 200:
            payment = Payment.objects.create(user=self.request.user, id=response_data["pidx"],amount=total_amount,quantity=total_quantity)
            payment.save()
            for product_detail in product_details:
                product = Product.objects.get(p_id=product_detail['id'])
                payment_product = PaymentProduct.objects.create(payment_id=payment,
                                                                amount=product_detail['total_price'],
                                                                quantity=product_detail['quantity'],
                                                                product=product)
                payment_product.save()

            response_data["message"] = "Success"
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        elif response.status_code == 400:
            raise ValidationError(response_data)
        
    @extend_schema(
        parameters=[
            OpenApiParameter(name='pidx',location=OpenApiParameter.QUERY, description='Product ID', required=False, type=str),
            OpenApiParameter(name='txnId',location=OpenApiParameter.QUERY, description='Product ID', required=False, type=str),
            OpenApiParameter(name='amount',location=OpenApiParameter.QUERY, description='Product ID', required=False, type=str),
            OpenApiParameter(name='mobile',location=OpenApiParameter.QUERY, description='Product ID', required=False, type=str),
            OpenApiParameter(name='purchase_order_id',location=OpenApiParameter.QUERY, description='Product ID', required=False, type=str),
            OpenApiParameter(name='purchase_order_name',location=OpenApiParameter.QUERY, description='Product ID', required=False, type=str),
            OpenApiParameter(name='transaction_id',location=OpenApiParameter.QUERY, description='Product ID', required=False, type=str),
        ],
    )
    def validate(self, request, *args, **kwargs):
        pidx = self.request.query_params.get("pidx")
        transaction_id = self.request.query_params.get("transaction_id")
        amount = self.request.query_params.get("amount")
        if pidx and transaction_id and amount:
            payload = {
                "pidx": pidx
            }
            headers = {
                "Authorization" : settings.KHALTI_API_KEY
            }
            try:
                payment = Payment.objects.get(id=pidx)
            except Payment.DoesNotExist:
                # Handle the case when the Payment object does not exist
                # For example, return an error response or perform some other action
                return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
            if(payment.transaction_id == None and payment.amount != None):
                try:
                    response = requests.post(url=settings.PAYMENT_LOOKUP_URL, data=payload, headers=headers)
                    response_data = response.json()
                except Exception as e:
                    raise exceptions.ServiceUnavailable()
                
                if(response_data['status'] == "Completed"):
                    payment.status = response_data['status']
                    payment.transaction_id = response_data['transaction_id']
                    payment.amount = float(amount)/100
                    payment_products = PaymentProduct.objects.filter(payment_id = response_data['pidx'])
                    for payment_product in payment_products:
                        product = Product.objects.get(p_id=payment_product.product.p_id)
                        product.stock -= payment_product.quantity
                        product.save()
                    try:
                        Cart.objects.filter(user=self.request.user).delete()
                        
                    except:
                        return HttpResponseForbidden("You are not authorized")
                    payment.save()
                else:
                    print("NC")
            serializer = self.get_serializer(payment)
            return Response(serializer.data)
        
        return Response({'error':'payment not found'},status=status.HTTP_400_BAD_REQUEST)