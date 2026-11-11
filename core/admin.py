from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Application, Area, Company, Notification, Offer, StudentProfile, User


# HU10: activar / suspender / eliminar usuarios (is_active) y gestionar áreas.
@admin.register(User)
class PPOLUserAdmin(UserAdmin):
    list_display = ("email", "first_name", "role", "is_active")
    list_filter = ("role", "is_active")
    fieldsets = UserAdmin.fieldsets + (("Rol", {"fields": ("role",)}),)


admin.site.register([Area, Company, StudentProfile, Offer, Application, Notification])
