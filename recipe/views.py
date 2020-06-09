from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

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

  def get_serializer_class(self):
    """Return appropriate serializer class"""
    if self.action == 'retrieve':
      return serializers.RecipeDetailSerializer
    elif self.action == 'upload_image':
      return serializers.RecipeImageSerializer
    
    return self.serializer_class

  def perform_create(self, serializer):
    """Create new recipe"""
    serializer.save(user=self.request.user)

  @action(methods=['POST'], detail=True, url_path='upload-image')
  def upload_image(self, request, pk=None):
    """Upload image to recipe"""
    recipe = self.get_object()
    serializer = self.get_serializer(
      recipe,
      data=request.data
    )

    if serializer.is_valid():
      serializer.save()
      return Response(
        serializer.data,
        status.HTTP_200_OK
      )
    
    return Response(
      serializer.errors,
      status.HTTP_400_BAD_REQUEST
    )