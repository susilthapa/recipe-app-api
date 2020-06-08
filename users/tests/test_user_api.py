from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status 



CREATE_USER_URL = reverse('users:create')
TOKEN_URL = reverse('users:token')
ME_URL = reverse('users:me')

def create_user(**params):
  """Helper function to call multiple times"""
  return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase): 
  """Test the users API (public i.e unauthenticated)"""

  def setUp(self):
    self.client = APIClient()


  def test_create_valid_user_success(self):
    """Test creating user with valid payload is successful"""
    payload = {
      'email': 'testuser@gmail.com',
      'password': 'testpass123',
      'name': 'Test Name'
    }

    res = self.client.post(CREATE_USER_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    
    user = get_user_model().objects.get(**res.data)

    self.assertTrue(user.check_password(payload['password']))
    self.assertNotIn('password', res.data)


  def test_user_exists(self):
    """Creating user that already exists"""
    payload = {
      'email': 'testuser@gmail.com',
      'password': 'testpass123',
    }

    create_user(**payload)

    res = self.client.post(CREATE_USER_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


  def test_password_too_short(self):
    """Pass must be More tha five characters"""
    payload = {
        'email': 'testuser@gmail.com',
        'password': 'test',
      }
    res = self.client.post(CREATE_USER_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    user_exists = get_user_model().objects.filter(email=payload['email']).exists() 
    # remember each test refresh db /executes on own 
    self.assertFalse(user_exists) 


  def test_create_token_for_user(self):
    """Test that a token is created for user"""
    payload = {
      'email': 'test@gmail.com',
      'password': 'testpass123'
    }
    create_user(**payload)
    res = self.client.post(TOKEN_URL, payload)

    self.assertIn('token', res.data)
    self.assertEqual(res.status_code, status.HTTP_200_OK)


  def test_create_token_invalid_credentials(self):
    """Test tha token is not created if invalid credentials are given"""
    create_user(email='test@gmail.com', password='testpass123')
    payload = {
      'email': 'test@gmail.com',
      'password': 'wrongpass'
    }

    res = self.client.post(TOKEN_URL, payload)
    self.assertNotIn('token', res.data)
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
  

  def test_token_for_no_user(self):
    """Test that token is not created if user doesn't exists"""
    payload = {
      'email': 'test@gmail.com',
      'password': 'testpass123'
    }

    res = self.client.post(TOKEN_URL, payload)
    self.assertNotIn('toekn', res.data)
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  
  def test_create_token_missing_fields(self):
    """Test that email and password are required"""
    res = self.client.post(TOKEN_URL, {'email': 'com', 'password': ''})

    self.assertNotIn('token', res.data)
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_retrieve_user_unauthorized(self):
    """Test that user authentication is required for users"""
    res = self.client.get(ME_URL)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
  """Test api requests that requires authentiaction"""

  def setUp(self):
    self.user = create_user(
      email="testuser@gmail.com",
      password="testpass123",
      name="Test User"
    )
    self.client = APIClient()
    self.client.force_authenticate(user=self.user)

  def test_retrieve_success(self):
    """Test retrieving profile for logged in user"""
    res = self.client.get(ME_URL)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, {
      'name': self.user.name,
      'email':self.user.email,

      })
  
  def test_post_moethod_not_allowed(self):
    """Test that POST is not allowed in me url"""
    res = self.client.post(ME_URL, {})

    self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED) 
  
  def test_update_user_profile(self):
    """Test updating the user profile for authenticated user"""
    payload = {'name':'New User', 'password':'newpassword123'}

    res = self.client.patch(ME_URL, payload)

    self.user.refresh_from_db()

    self.assertEqual(self.user.name, payload['name'])
    self.assertTrue(self.user.check_password(payload['password']))
    self.assertEqual(res.status_code, status.HTTP_200_OK)