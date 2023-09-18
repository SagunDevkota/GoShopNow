from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin,ListModelMixin,RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from drf_spectacular.openapi import OpenApiParameter
from drf_spectacular.utils import extend_schema

from address.serializers import AddressSerializer,DeliveryAddressSerializer
from core.models import Address,DeliveryAddress

class AddressViewSet(GenericViewSet,ListModelMixin):
    """Viewset for address model."""
    serializer_class = AddressSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Address.objects.all().order_by('parent')

    def get_queryset(self):
        if(self.request.method == "GET"):
            parent = (self.request.GET.get("parent"))
            queryset = super().get_queryset()
            queryset = queryset.filter(parent=parent)
        return queryset
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='parent',location=OpenApiParameter.QUERY, description='''Parent ID<br>
                            For provience parent->null<br> 
                            For city use provience ID<br> 
                            For area use city ID''', required=False, type=str),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
class DeliveryAddressViewSet(CreateModelMixin,GenericViewSet,ListModelMixin):
    """Viewset for delivery address model."""
    serializer_class = DeliveryAddressSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = DeliveryAddress.objects.all()

    def perform_create(self, serializer):
        delivery_address = self.queryset.filter(user=self.request.user).first()
        if(delivery_address):
            validated_data = serializer.validated_data
            delivery_address.provience = validated_data["provience"]
            delivery_address.city = validated_data["city"]
            delivery_address.area = validated_data["area"]
            delivery_address.save()
        else:
            serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset