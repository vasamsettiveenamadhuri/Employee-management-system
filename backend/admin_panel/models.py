from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import random
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from django.utils.timezone import now
from datetime import timedelta


# class CustomUser(AbstractUser):
#     username = models.CharField(max_length=150, unique=True)  # ✅ Required field
#     email = models.EmailField(unique=True)  # ✅ Used for authentication
#     designation = models.CharField(max_length=100, blank=True, null=True)
#     employee_id = models.CharField(max_length=10, unique=True, blank=True, null=True)
#     employee_name = models.CharField(max_length=100, blank=True, null=True)
#     join_date = models.DateField(blank=True, null=True)

#     USERNAME_FIELD = "email"  # ✅ Use email for authentication
#     REQUIRED_FIELDS = ["username"]  # ✅ Keep username required

#     def save(self, *args, **kwargs):
#         """Ensure that email is always stored in the username field."""
#         if not self.username:  
#             self.username = self.email  # ✅ Set username as email
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.username  # ✅ Returns email (same as username)



class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    employee_id = models.CharField(max_length=10, unique=True, blank=True, null=True)
    employee_name = models.CharField(max_length=100, blank=True, null=True)
    join_date = models.DateField(blank=True, null=True)
    photo = models.ImageField(
        upload_to='employee_photos/', 
        default='employee_photos/image.jpg',  # ✅ Default image
        blank=True, 
        null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


User=get_user_model()


class OTP(models.Model):
    User=get_user_model()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Added user field
    email = models.EmailField(unique=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        """Check if OTP is expired (valid for 5 minutes)"""
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return f"OTP for {self.email}: {self.otp_code}"



# Employee Model
class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    designation = models.CharField(blank=True, max_length=100)  # ✅ Fixed typo
    employee_id = models.CharField(max_length=10, unique=True)
    employee_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_of_joining = models.DateField()  # ✅ Keep this consistent

    def __str__(self):
        return self.employee_name
    


