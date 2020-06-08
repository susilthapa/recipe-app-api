from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
  """Serializer for ther users objects"""

  class Meta:
    model = get_user_model()
    fields = ('email', 'password', 'name')
    extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

  def create(self, validated_data):
    """Create a new user with encrypted password and return it"""
    return get_user_model().objects.create_user(**validated_data)
  
  def update(self, instance, validated_data): # instance is model instance linked to our model serializer
    """Update user, setting password correctly and return it"""
    password = validated_data.pop('password', None)
    user = super().update(instance, validated_data) # calling ModelSerializer update function
    
    if password:
      user.set_password(password)
      user.save()

    return user

class AuthTokenSerializer(serializers.Serializer):
  """Serializer for the user authentication object"""
  email = serializers.CharField()
  password = serializers.CharField(
    style={'input_type': 'password'},
    trim_whitespace=False
  )

  def validate(self, attrs): # attrs is every fields that makes up the serializer that passed as dict
    """Validate and authenticate the user"""
    email = attrs.get('email') 
    password = attrs.get('password')

    user = authenticate(
      request=self.context.get('request'),
      username=email,
      password=password
    )

    if not user:
      msg = _('Unable to authenticate with provided credentials')
      raise serializers.ValidationError(msg, code='authentication')
      
    attrs['user'] = user
    return attrs