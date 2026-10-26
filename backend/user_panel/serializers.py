

from rest_framework import serializers
from .models import TimeSheet
from .models import LeaveRequest, PermissionRequest
from rest_framework import serializers
from .models import UserProgress
from django.contrib.auth import get_user_model

User=get_user_model()

class TimeSheetSerializer(serializers.ModelSerializer):
    total_work_time = serializers.SerializerMethodField()
    total_break_time = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()  

    class Meta:
        model = TimeSheet
        fields = '__all__'

    def get_date(self, obj):
        return obj.clock_in_time.date() if obj.clock_in_time else None  

    def get_total_work_time(self, obj):
        return str(obj.calculate_total_work_time()) if obj.calculate_total_work_time() else "0:00:00"

    def get_total_break_time(self, obj):
        return str(obj.total_break_time) if obj.total_break_time else "0:00:00"




# class UserProgressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProgress
#         fields = ['id', 'user', 'start_time', 'end_time', 'description', 'date']
#         read_only_fields = ['user', 'date']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_superuser", "employee_id", "designation", "join_date"]



class UserProgressSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # ✅ Nest user details

    class Meta:
        model = UserProgress
        fields = ["user", "date", "tasks"]




class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = '__all__'  # Ensure all fields are included

    def create(self, validated_data):
        request = self.context.get('request')  # Get the request context
        validated_data['user'] = request.user  # Assign the logged-in user
        return super().create(validated_data)


class PermissionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionRequest
        fields = '__all__'
        
        
from rest_framework import serializers
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()  # Custom field for employee details

    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'clock_in', 'clock_out', 'total_hours', 'attendance_status']
        read_only_fields = ['total_hours', 'attendance_status']

    def get_employee(self, obj):
        return {
            "id": obj.employee.id,
            "username": obj.employee.username
        } if obj.employee else None


