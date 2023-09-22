"""
Tests for game API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core.models import DiscountCoupon
from unittest import mock

GAME_URL = reverse('game:slotmachine')

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

class TestPrivateGameAPI(TestCase):
    """Test case for slot machine api."""

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
        return super().setUp()
    
    def test_game_invalid_bet(self):
        """Test slot machine endpoint for invalid bet"""
        response = self.client.get(GAME_URL+"?bet=32")

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(),{"error":"Invalid Bet"})

    def test_game_without_bet(self):
        """Test slot machine if bet not mentioned."""
        response = self.client.get(GAME_URL)

        self.assertEqual(response.status_code,status.HTTP_428_PRECONDITION_REQUIRED)
        self.assertEqual(response.json(),{"error":"Bet not found"})

    def test_game_with_less_reward_point(self):
        """Test slot machine with insufficient reward points."""
        self.user.reward_points = 20
        self.user.save()

        response = self.client.get(GAME_URL+"?bet=50")

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(),{"error":"Insufficient Reward Points"})

    def test_game_success(self):
        """Test game with valid bet and sufficient reward point"""
        self.user.reward_points = 20
        self.user.save()

        response = self.client.get(GAME_URL+"?bet=10")

        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertIn("response",response.json().keys())

    @mock.patch('game.slot_machine.random.choice',return_value=1)
    def test_game_with_win_success(self,mock_play_game):
        """Test game with valid bet and sufficient reward point and won bet."""
        self.user.reward_points = 20
        self.user.save()

        response = self.client.get(GAME_URL+"?bet=10")
        coupon = DiscountCoupon.objects.get(user=self.user)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertIsNotNone(coupon)

