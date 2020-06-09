from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers


class BaseRecipeAttributeViewSet(viewsets.GenericViewSet, 
                                mixins.ListModelMixin,
                                mixins.CreateModelMixin,
                                ):
  """Base viewset fot user owned recipe viewset"""
  authentication_classes = (TokenAuthentication,)
  permission_classes = (IsAuthenticated,)

  def get_queryset(self):
    """Return obj for current authenticated user"""
    return self.queryset.filter(user=self.request.user).order_by('-name')

  def perform_create(self, serializer):
    """Create new ingredient"""
    serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttributeViewSet):
  """Manage tags in the database"""
 
  queryset = Tag.objects.all()
  serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttributeViewSet):
  """Manage Ingredients in the database"""
  queryset = Ingredient.objects.all()
  serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
  """Manage recipe in database"""
  serializer_class = serializers.RecipeSerializer
  authentication_classes = (TokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  queryset = Recipe.objects.all()

  def get_queryset(self):
    """Retrieve recipies for authenticated user"""
    return self.queryset.filter(user=self.request.user)