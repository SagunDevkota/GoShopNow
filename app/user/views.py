"""
Views for the user API
"""

from rest_framework import generics, permissions

from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import make_password

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