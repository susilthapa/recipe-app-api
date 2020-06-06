from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from core import models

class UserAdmin(BaseUserAdmin):
  ordering = ['id']
  list_display = ['email', 'name']
  fieldsets = (
      (None, {'fields': ('email', 'password'),}),
      (_('Personal Info'),{'fields':('name',)}),  # one itime fields therefore comma 
      (
        _('Permissions'),
        {'fields':('is_active', 'is_staff', 'is_superuser')}
      ),
      (_('Important dates'),{'fields':('last_login',)})
  )
  add_fieldsets = (
    (None, {
      'classes': ('wide',),
      'fields': ('email', 'password1', 'password2') # by default add page contains username but not our User model
    }), # one item in the add_fieldsets therefore comma otherwise python get confused of it is object
  )
  
admin.site.register(models.User, UserAdmin)