from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


RECIPE_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
  """Return recipe detail url"""
  return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_tag(user, name='Main Course'):
  """Create and return a sample tag"""
  return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='Cinnamon'):
  """Create and return a sample ingredient"""
  return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
  """Create and return sample recipe"""
  defaults = {
    'title':'Sample Recipe',
    'time_minutes':10,
    'price': 5.00
  }
  defaults.update(params)

  return Recipe.objects.create(user=user, **defaults) # ** converts dict-->args and vice-versa


class PublicRecipeApiTests(TestCase):
  """Test unauthenticated recipe API access"""

  def setUp(self):
    self.client = APIClient()

  def test_auth_required(self):
    """Test tha authentication is required"""
    res =  self.client.get(RECIPE_URL)
    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTests(TestCase):
  """Test authenticated recipe api access"""

  def setUp(self):
    self.client = APIClient()
    self.user = get_user_model().objects.create_user(email='test@gmail.com', password='testpass123')
    self.client.force_authenticate(self.user)

  def test_retrieve_recipes(self):
    """Test retrieving list of recipes"""
    sample_recipe(user=self.user)
    sample_recipe(user=self.user)

    res = self.client.get(RECIPE_URL)
    recipe = Recipe.objects.all().order_by('-id')
    serializer = serializers.RecipeSerializer(recipe, many=True)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    # self.assertEqual(res.data, serializer.data)

  def test_limited_to_auth_user(self):
    """Test retriving for auth uesr only"""
    user2 = get_user_model().objects.create_user(email='new@gmail.com', password='new12333')

    sample_recipe(user=user2)
    sample_recipe(user=self.user)

    res = self.client.get(RECIPE_URL)

    recipes = Recipe.objects.filter(user=self.user)
    serializer = serializers.RecipeSerializer(recipes, many=True)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(len(res.data), 1)
    self.assertEqual(res.data, serializer.data)

  def test_view_recipe_detail(self):
    """Test viewing a recipe detail"""
    recipe = sample_recipe(user=self.user)
    recipe.tags.add(sample_tag(user=self.user))
    recipe.ingredients.add(sample_ingredient(user=self.user))

    url = detail_url(recipe.id)
    res = self.client.get(url)

    serializer = serializers.RecipeDetailSerializer(recipe)
    self.assertEqual(res.data, serializer.data)