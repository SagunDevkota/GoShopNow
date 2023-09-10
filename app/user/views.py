"""
Views for the user API
"""

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import (
    UserSerializer,
    UserDetailsSerializer
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return UserSerializer
        else:
            return UserDetailsSerializer
        
class ActivateAccountView(generics.RetrieveAPIView):
    """
    Activate the user account.
    """
    def get(self, request, *args, **kwargs):
        print(kwargs)
        if('token' in kwargs.keys()):
            user = get_object_or_404(get_user_model().objects.filter(token=kwargs["token"]))
            user.is_active = True
            user.save()
            return Response({'message': 'Account activated'}, status=status.HTTP_200_OK)
        else:
            return Response({'error':'Token Required'},status=status.HTTP_400_BAD_REQUEST)
