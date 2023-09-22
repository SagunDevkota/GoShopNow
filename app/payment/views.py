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

from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings

from core.tasks import send_email

from core.models import Payment,Product,Cart,PaymentProduct,User,DiscountCoupon
from core.pagination import CustomPagination
from core.services.mail_sender import send_email
from core.services.pdf_generator import generate
from payment import serializers,exceptions

import uuid
import os
import requests

def generate_unique_id():
    return str(uuid.uuid4())

class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):        
        if view.action == 'validate':
            return True  # Allow all GET requests without authentication
        if view.action == "download":
            return True
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
        items = list(Cart.objects.filter(user=self.request.user).values())
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
        coupon = None
        discount_amount = 0
        if("coupon_code" in data.keys()):
                coupon = DiscountCoupon.objects.filter(user=self.request.user,coupon_code=data["coupon_code"],used=False).first()
                if(coupon):
                    coupon.used = True
                    amount = total_amount
                    if(amount*coupon.max_percentage/100 > coupon.max_amount):
                        total_amount -= coupon.max_amount
                        discount_amount = coupon.max_amount
                    else:
                        total_amount -= amount*coupon.max_percentage/100
                        discount_amount = amount*coupon.max_percentage/100
                    coupon.save()
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
            payment = Payment.objects.create(user=self.request.user, id=response_data["pidx"],amount=total_amount,quantity=total_quantity,coupon=coupon,discount_amount=discount_amount)
            
            for product_detail in product_details:
                product = Product.objects.get(p_id=product_detail['id'])
                payment_product = PaymentProduct.objects.create(payment_id=payment,
                                                                amount=product_detail['total_price'],
                                                                quantity=product_detail['quantity'],
                                                                product=product)
                payment_product.save()

            response_data["message"] = "Success"
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError(response_data)
        
    @extend_schema(
        parameters=[
            OpenApiParameter(name='pidx',location=OpenApiParameter.QUERY, description='pidx', required=False, type=str),
            OpenApiParameter(name='txnId',location=OpenApiParameter.QUERY, description='txnId', required=False, type=str),
            OpenApiParameter(name='amount',location=OpenApiParameter.QUERY, description='amount', required=False, type=str),
            OpenApiParameter(name='mobile',location=OpenApiParameter.QUERY, description='mobile', required=False, type=str),
            OpenApiParameter(name='purchase_order_id',location=OpenApiParameter.QUERY, description='Purchase Order ID', required=False, type=str),
            OpenApiParameter(name='purchase_order_name',location=OpenApiParameter.QUERY, description='Purchase Order Name', required=False, type=str),
            OpenApiParameter(name='transaction_id',location=OpenApiParameter.QUERY, description='Transaction ID', required=False, type=str),
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
                return Response({"error": "Payment not found"}, status=status.HTTP_400_BAD_REQUEST)
            if(payment.transaction_id == None and payment.amount != None):
                try:
                    response = requests.post(url=settings.PAYMENT_LOOKUP_URL, data=payload, headers=headers)
                except Exception as e:
                    raise exceptions.ServiceUnavailable()
                if(response.status_code == status.HTTP_200_OK):
                    response_data = response.json()
                    if(response_data["status"] == "Completed"):
                        payment.status = response_data['status']
                        payment.transaction_id = response_data['transaction_id']
                        payment.amount = float(amount)/100
                        payment_products = PaymentProduct.objects.filter(payment_id = response_data['pidx'])
                        payment_detail_list = [['Product Name','Unit Price','Units','Subtotal']]
                        for payment_product in payment_products:
                            product = Product.objects.get(p_id=payment_product.product.p_id)
                            product.stock -= payment_product.quantity
                            if(product.stock < product.threshold):
                                send_email.delay("Threshold Reached",f"The product {product.name} with id: {product.p_id} is going out of stock.",[settings.EMAIL_HOST_USER],'')
                            product.save()

                            payment_detail_list.append([product.name,product.price,payment_product.quantity,payment_product.amount])
                        payment_detail_list.append(['Discount',None,None,payment.discount_amount*-1])
                        generate(response_data['pidx']+'.pdf',payment_detail_list,response_data['transaction_id'])
                        Cart.objects.filter(user=payment.user).delete()
                        user = User.objects.get(id=payment.user.id)
                        user.reward_points += payment.amount/100
                        user.save()
                        payment.save()
                    else:
                        return Response({"error":"Payment Not Completed"},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error":"Bad Request"},status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(payment)
            return Response(serializer.data)
        return Response({'error':'Invalid Request'},status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(
    parameters=[
        OpenApiParameter(name='id',location=OpenApiParameter.QUERY, description='Payment ID', required=False, type=str),
        ]
    )
    def download(self,request,*args,**kwargs):
        payment = get_object_or_404(Payment,id=request.query_params["id"],status="Completed",user=self.request.user)
        file_name = payment.id+".pdf"
        file_path = os.path.join(settings.INVOICES_PATH,file_name)
        if(os.path.exists(file_path)):
            try:
                with open(file_path, 'rb') as file:
                    response = HttpResponse(file, content_type='pdf')
                    response['Content-Disposition'] = f'attachment; filename={file_name}'
                    return response
            except:
                return Response({"error":"Error reading file."},status=status.HTTP_500_INTERNAL_SERVER_ERROR)