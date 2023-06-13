"""View for review model"""

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import BasePermission
from rest_framework import status
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from rest_framework_simplejwt.authentication import JWTAuthentication

from payment import serializers,exceptions

from core.models import Payment,Product
from core.pagination import CustomPagination

import requests

from django.conf import settings
from django.urls import reverse

class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        print(view.action)
        print(request.method)
        
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
        product = serializer.validated_data.get("product",None)
        quantity = serializer.validated_data.get("quantity",None)
        amount = product.price*quantity*100
        payload = {
            "purchase_order_id":product.p_id,
            "purchase_order_name":product.name,
            "amount":product.price*quantity*100, #convert to paisa
            "return_url": self.request.build_absolute_uri(reverse('payment:validate')),
            "website_url": self.request.build_absolute_uri("/")
        }
        headers = {
            "Authorization" : settings.KHALTI_API_KEY
        }
        try:
            response = requests.post(url=settings.PAYMENT_URL, data=payload, headers=headers)
            response_data = response.json()
        except:
            raise exceptions.ServiceUnavailable()
        if response.status_code == 200:
            serializer.save(user=self.request.user, id=response_data["pidx"],amount=amount)
            response_data["message"] = "Success"
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        elif response.status_code == 400:
            raise ValidationError(response_data)
        
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
                    if(response_data['status'] == "Completed"):
                        payment.status = response_data['status']
                        payment.transaction_id = response_data['transaction_id']
                        payment.amount = float(amount)/100
                        product = Product.objects.get(p_id = payment.product.p_id)
                        product.stock -= payment.quantity
                        product.save()
                        payment.save()
                    else:
                        print("NC")
                except Exception as e:
                    raise exceptions.ServiceUnavailable()
            serializer = self.get_serializer(payment)
            return Response(serializer.data)
        
        return Response({'error':'payment not found'},status=status.HTTP_400_BAD_REQUEST)