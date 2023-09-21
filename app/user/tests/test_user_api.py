"""
Tests for user API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status,serializers



CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token_obtain_pair')
TOKEN_REFRESH = reverse('user:token_refresh')
PROFILE_URL = reverse('user:profile')

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Test the public features of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        payload = {
            "first_name" : "xyz",
            "last_name" : "abc",
            "phone" : "1234",
            "email" : "user@example.com",
            "password" : "Test123@@@"
        }
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists"""
        payload = {
            "first_name" : "xyz",
            "last_name" : "abc",
            "phone" : "1234",
            "email" : "user@example.com",
            "password" : "test123"
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test error returned if password is too short."""
        payload = {
            "first_name" : "xyz",
            "last_name" : "abc",
            "phone" : "1234",
            "email" : "user@example.com",
            "password" : "test"
        }

        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists,False)

    def test_create_token_for_user(self):
        """Create token if user exists"""
        payload = {
            "first_name" : "xyz",
            "last_name" : "abc",
            "phone" : "1234",
            "email" : "user@example.com",
            "password" : "test123"
        }

        user = create_user(**payload)
        user.is_active = True
        user.save()

        creds = {
            "email" : "user@example.com",
            "password" : "test123"
        }

        res = self.client.post(TOKEN_URL,creds)

        self.assertIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test token not generated for bad credentials."""
        payload = {
            "first_name" : "xyz",
            "last_name" : "abc",
            "phone" : "1234",
            "email" : "user@example.com",
            "password" : "test123"
        }

        create_user(**payload)

        creds = {
            "email" : "user@example.com",
            "password" : "test12"
        }

        res = self.client.post(TOKEN_URL,creds)

        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_for_blank_password(self):
        """Test token for blank password"""
        payload = {
            "email" : "user@example.com",
            "password" : ""
        }
        res = self.client.post(TOKEN_URL,payload)

        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_user_unauthorized(self):
        """Test get profile for unauthenticated user."""

        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_incorrect_token_in_account_activation(self):
        """Return error if activation token provided is incorrect."""
        payload = {
            "first_name" : "xyz",
            "last_name" : "abc",
            "phone" : "1234",
            "email" : "user2@example.com",
            "password" : "test123"
        }
        user = create_user(**payload)
        activation_url = reverse('user:activate-account',args=["xyz"])
        res = self.client.get(activation_url)
        self.assertEqual(res.status_code,status.HTTP_404_NOT_FOUND)
        self.assertIn("detail",res.json().keys())

    def test_correct_token_in_account_activation(self):
        """Return error if activation token provided is incorrect."""
        payload = {
            "first_name" : "xyz",
            "last_name" : "abc",
            "phone" : "1234",
            "email" : "user2@example.com",
            "password" : "test123"
        }
        user = create_user(**payload)
        activation_url = reverse('user:activate-account',args=[user.token])
        res = self.client.get(activation_url)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn("message",res.json().keys())

    def test_get_refresh_token_success(self):
        """Test generate referesh token"""
        payload = {
            "first_name" : "xyz",
            "last_name" : "abc",
            "phone" : "1234",
            "email" : "user1@example.com",
            "password" : "test123"
        }

        user = create_user(**payload)
        user.is_active = True
        user.save()

        res = self.client.post(TOKEN_URL,data={"email":payload["email"],"password":payload["password"]})
        res2 = self.client.post(TOKEN_REFRESH,data={"refresh":res.json()["refresh"]})
        self.assertIn("access",res2.json().keys())

class PrivateUserApiTests(TestCase):
    """Test API requests that require authenticaation."""

    payload = {
            "first_name" : "xyz",
            "last_name" : "abc",
            "phone" : "1234",
            "email" : "user@example.com",
            "password" : "test123"
        }
    
    def setUp(self):
        self.user = create_user(**self.payload)
        self.user.is_active = True
        self.user.save()
        self.client = APIClient()
        user = {
            "email":self.user.email,
            "password":self.payload["password"]
        }
        self.res = self.client.post(TOKEN_URL,user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        header = {
            "Authorization":"Bearer "+self.res.json()["access"]
        }

        res = self.client.get(PROFILE_URL,headers=header)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res_data = {'first_name' : res.json()['first_name'],
                    'email' : res.json()['email']}
        self.assertEqual(res_data,{
            'first_name' : self.user.first_name,
            'email' : self.user.email,
        })

    def test_post_profile_not_allowed(self):
        """Test POST is not allowed for the endpoint."""
        res = self.client.post(PROFILE_URL,{})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authentication."""
        payload = {'first_name':'updated name', 'password':'newpassword123'}
        header = {
            "Authorization":"Bearer "+self.res.json()["access"]
        }
        res = self.client.patch(PROFILE_URL, payload,headers=header)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, payload['first_name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_without_activation(self):
        """Throw error if profile is not activated."""
        payload = {
            "first_name" : "xyz",
            "last_name" : "abc",
            "phone" : "1234",
            "email" : "user1@example.com",
            "password" : "test123"
        }

        create_user(**payload)
        creds = {
            "email":payload["email"],
            "password":payload["password"]
        }
        res = self.client.post(TOKEN_URL,creds)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail",res.json().keys())
