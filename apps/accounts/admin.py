from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class OficioProUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("OficioPro", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("OficioPro", {"fields": ("email", "role")}),)
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
