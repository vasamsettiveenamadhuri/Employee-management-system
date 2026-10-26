from django.contrib import admin
from .models import CustomUser, Employee,OTP  # Import your models

# Register models to Django Admin
admin.site.register(CustomUser)
admin.site.register(Employee)
admin.site.register(OTP)
