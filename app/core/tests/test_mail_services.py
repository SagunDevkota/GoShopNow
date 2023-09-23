"""
Tests for mail sender.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from core.services import mail_sender
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from unittest import mock
from product.serializers import ProductSerializer

class TestMailSender(TestCase):
    """Tests for sending email"""

    def test_mail_sent_no_info(self):
        """Test when all info is not provided"""
        response = mail_sender.send_email(None,"message",['xyz@example.com'],'')
        self.assertEqual(response,False)

    @mock.patch('core.services.mail_sender.open',return_value=IOError)
    def test_mail_sent_service_down(self,mock_send):
        """Test send mail when smtp server is down"""
        response = mail_sender.send_email("hi","message",['xyz@example.com'],'path')
        self.assertEqual(response,False)

    def test_send_mail_success(self):
        """Test send email successfully."""
        response = mail_sender.send_email('True',"message",['xyz@example.com'],'')
        self.assertEqual(response,True)

    def test_send_mail_with_attachment_success(self):
        """Test send email successfully."""
        response = mail_sender.send_email('True',"message",['xyz@example.com'],'xyz.pdf')
        self.assertEqual(response,True)