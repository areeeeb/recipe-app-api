from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicApiTests(TestCase):
    """Tests the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload succeeds"""
        payload = {
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'test user'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {'email': 'test@example.com', 'password': 'password123'}
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password must be more than 5 characters"""
        payload = {'email': 'test@example.com', 'password': 'pass'}

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_generate_token_on_login(self):
        """Test that the token is generated when the user logs in"""
        payload = {'email': 'test@example.com', 'password': 'testpass123'}
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_generate_token_on_invalid_credentials(self):
        """Test that the token is not generated if invalid credentials are
        provided"""
        payload = {'email': 'test@example.com', 'password': 'testpass123'}
        create_user(**payload)

        res = self.client.post(TOKEN_URL, {
            'email': 'test@example.com', 'password': 'wrongpass123'
        })

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_token_on_no_user(self):
        """Test that the token is not generated if user doesn't exist"""
        res = self.client.post(TOKEN_URL, {
            'email': 'random@example.com',
            'password': 'wrongpasshehe'
        })

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_token_on_missing_credentials(self):
        """Test that the token is not generated if the credentials are
        missing"""
        res = self.client.post(TOKEN_URL, {
            'email': 'test@example.com',
            'password': ''
        })

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
