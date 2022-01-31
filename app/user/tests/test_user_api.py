import email
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    """util function to create user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users api public"""

    def setUp(self):
        self.client = APIClient()
        self.user1_payload = {
            'email': 'test1@gmail.com',
            'password': 'test1@123',
            'name': 'Test1'
        }
        self.user2_payload = {
            'email': 'test2@gmail.com',
            'password': 'test2@123',
        }

    def test_create_valid_user_success(self):
        """Test user with valid payload success"""
        res = self.client.post(CREATE_USER_URL, self.user1_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(self.user1_payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_user_already_exist(self):
        """Test create user already exists in the database"""
        create_user(**self.user1_payload)
        res = self.client.post(CREATE_USER_URL, self.user1_payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test shot password while creating the user"""
        payload = self.user1_payload
        payload['password'] = "123"
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        create_user(**self.user2_payload)
        res = self.client.post(TOKEN_URL, self.user2_payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_invalid_credentials(self):
        """Test that token is not create if the invalid credentials are given"""
        create_user(**self.user2_payload)

        payload = self.user2_payload
        payload['password'] = 'incorrectpassword'
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not create if user doesn't exists"""
        res = self.client.post(TOKEN_URL, self.user2_payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        payload = self.user2_payload
        del payload['password']
        
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
