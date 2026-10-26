
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from rest_framework import serializers
from user_panel.models import LeaveRequest,PermissionRequest


User = get_user_model()

# class EmployeeRegisterSerializer(serializers.ModelSerializer):
#     employee_name = serializers.CharField(required=True)
#     designation = serializers.CharField(required=True)
#     employee_id = serializers.CharField(required=True)
#     join_date = serializers.DateField(required=True)
#     password = serializers.CharField(write_only=True)
#     is_admin = serializers.BooleanField(write_only=True, required=False, default=False)  # Accept is_admin

#     class Meta:
#         model = User  # ✅ Use CustomUser instead of User
#         fields = ["email", "password", "username", "employee_name", "designation", "employee_id", "join_date", "is_admin"]
#         extra_kwargs = {
#             "username": {"read_only": True},  # ✅ Username is auto-filled with email
#         }

#     def create(self, validated_data):
#         email = validated_data["email"]

#         # ✅ Check for duplicate email before proceeding
#         if User.objects.filter(email=email).exists():
#             raise serializers.ValidationError({"message": "Mail already exists"})

#         # Extract fields
#         employee_name = validated_data.pop("employee_name")
#         designation = validated_data.pop("designation")
#         employee_id = validated_data.pop("employee_id")
#         join_date = validated_data.pop("join_date")
#         is_admin = validated_data.pop("is_admin", False)  # Default to False if not provided

#         # ✅ Create user and set username = email
#         user = User.objects.create_user(
#             email=email,
#             username=email,  # ✅ Auto-fill username with email
#             password=validated_data["password"],
#             is_superuser=is_admin,  # ✅ Set superuser flag based on is_admin
#             is_staff=True,  # ✅ All employees are staff
#             is_active=True,
#             employee_name=employee_name,
#             designation=designation,
#             employee_id=employee_id,
#             join_date=join_date,
#         )

#         return user

# from rest_framework import serializers
# from .models import CustomUser  # ✅ Use CustomUser instead of User

# class EmployeeRegisterSerializer(serializers.ModelSerializer):
#     employee_name = serializers.CharField(required=True)
#     designation = serializers.CharField(required=True)
#     employee_id = serializers.CharField(required=True)
#     join_date = serializers.DateField(required=True)
#     password = serializers.CharField(write_only=True)
#     is_admin = serializers.BooleanField(write_only=True, required=False, default=False)  # ✅ Accept is_admin
#     photo = serializers.ImageField(required=False)  # ✅ Allow photo upload

#     class Meta:
#         model = CustomUser  # ✅ Use CustomUser model
#         fields = ["email", "password", "username", "employee_name", "designation", "employee_id", "join_date", "is_admin", "photo"]
#         extra_kwargs = {
#             "username": {"read_only": True},  # ✅ Username is auto-filled with email
#         }

#     def create(self, validated_data):
#         email = validated_data["email"]

#         # ✅ Check for duplicate email before proceeding
#         if CustomUser.objects.filter(email=email).exists():
#             raise serializers.ValidationError({"message": "Email already exists"})

#         # Extract additional fields
#         employee_name = validated_data.pop("employee_name")
#         designation = validated_data.pop("designation")
#         employee_id = validated_data.pop("employee_id")
#         join_date = validated_data.pop("join_date")
#         is_admin = validated_data.pop("is_admin", False)  # ✅ Default to False if not provided
#         photo = validated_data.pop("photo", None)  # ✅ Get photo if provided

#         # ✅ Create user and set username = email
#         user = CustomUser.objects.create_user(
#             email=email,
#             username=email,  # ✅ Auto-fill username with email
#             password=validated_data["password"],
#             is_superuser=is_admin,  # ✅ Set superuser flag based on is_admin
#             is_staff=True,  # ✅ All employees are staff
#             is_active=True,
#             employee_name=employee_name,
#             designation=designation,
#             employee_id=employee_id,
#             join_date=join_date,
#             photo=photo  # ✅ Store the uploaded photo
#         )

#         return user


from django.conf import settings

class EmployeeRegisterSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(required=True)
    designation = serializers.CharField(required=True)
    employee_id = serializers.CharField(required=True)
    join_date = serializers.DateField(required=True)
    password = serializers.CharField(write_only=True)
    is_admin = serializers.BooleanField(write_only=True, required=False, default=False)
    photo = serializers.ImageField(required=False)  

    class Meta:
        model = User  
        fields = ["email", "password", "username", "employee_name", "designation", "employee_id", "join_date", "is_admin", "photo"]
        extra_kwargs = {
            "username": {"read_only": True},  
        }

    def create(self, validated_data):
        email = validated_data["email"]

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"message": "Email already exists"})

        employee_name = validated_data.pop("employee_name")
        designation = validated_data.pop("designation")
        employee_id = validated_data.pop("employee_id")
        join_date = validated_data.pop("join_date")
        is_admin = validated_data.pop("is_admin", False)  
        photo = validated_data.pop("photo", None)  

        user = User.objects.create_user(
            email=email,
            username=email,  
            password=validated_data["password"],
            is_superuser=is_admin,  
            is_staff=True,  
            is_active=True,
            employee_name=employee_name,
            designation=designation,
            employee_id=employee_id,
            join_date=join_date,
            photo=photo  
        )

        return user  

    def to_representation(self, instance):
        """ Ensure that the photo field returns the full URL. """
        data = super().to_representation(instance)
        request = self.context.get("request")  # Get request object

        if instance.photo:
            photo_url = instance.photo.url
            if request is not None:
                photo_url = request.build_absolute_uri(photo_url)  # Convert to full URL
            data["photo"] = photo_url  # Return full URL for the frontend

        return data




class EmployeeLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # ✅ Authenticate user
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        # ✅ Check if the user is active
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")

        data["user"] = user
        return data
    



class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "employee_name",
            "email",
            "designation",
            "employee_id",
            "join_date",
            "is_admin",
            "password",
            "photo",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},  # Hide password in responses
        }
        

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        employee = User(**validated_data)
        if password:
            employee.set_password(password)  # Hash the password
        employee.save()
        return employee

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # Hash the password if updated
        instance.save()
        return instance


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is associated with this email.")
        return value


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match!")
        return data


class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['status', 'user']  # Prevent users from modifying status and user

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user  # Assign the logged-in user
        return super().create(validated_data)



class PermissionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionRequest
        fields = '__all__'
        read_only_fields = ['status', 'user']  # Prevent users from modifying status and user

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user  # Assign the logged-in user
        return super().create(validated_data)
    


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        
class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = [
            "id", "leave_type", "start_date", "end_date", "is_half_day",
            "leave_mode", "date_of_attending_office", "reason", "status"
        ]

class PermissionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionRequest
        fields = [
            "id", "absence_type", "permission_start_date", "permission_end_date",
            "compensation_start", "compensation_end", "reason", "status"
        ]