"""
Serializers for the user API View.
"""
from django.contrib.auth import (
        get_user_model,
        authenticate
    )
from django.utils.translation import gettext as _

from rest_framework import serializers

from rest_framework_simplejwt.tokens import RefreshToken


class PasswordValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user_email):
        if len(password) < self.min_length:
            raise serializers.ValidationError(f"The password must be at least {self.min_length} characters long.")

        if not any(char.isupper() for char in password):
            raise serializers.ValidationError("The password must contain at least one capital letter.")

        if not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~" for char in password):
            raise serializers.ValidationError("The password must contain at least one special character.")

        if user_email.lower() in password.lower():
            raise serializers.ValidationError("The password must not contain the email address.")

        return password

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email','password','first_name','last_name','phone']
        extra_kwargs = {'password': 
                        {'write_only':True,'min_length':5}
                        }
        
    def validate(self, attrs):
        email = attrs.get('email', None)
        password = attrs.get('password', None)

        if email and password:
            password_validator = PasswordValidator()
            password = password_validator.validate(password, email)

        attrs['password'] = password
        return attrs
        
    def create(self,validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)
    
    def update(self,instance,validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
    
class UserDetailsSerializer(serializers.ModelSerializer):
    """Serializer with all user details"""
    class Meta:
        model = get_user_model()
        fields = ["id","last_login","is_superuser","first_name","last_name","phone","email","is_active","is_staff","is_superuser"]
        extra_kwargs = {'password': 
                        {'write_only':True,'min_length':5}
                        }
    
    def validate(self, attrs):
        email = attrs.get('email', None)
        password = attrs.get('password', None)

        if email and password:
            password_validator = PasswordValidator()
            password = password_validator.validate(password, email)

        attrs['password'] = password
        return attrs

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type':"password"},
        trim_whitespace=False,
    )

    def validate(self,attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        
        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code="authorization")
        
        attrs['user'] = user
        
        return attrs
    
    def get_token(self, user):
        """Retrieve the access token and refresh token for the user."""
        refresh = RefreshToken.for_user(user)
        tokens = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
        return tokens