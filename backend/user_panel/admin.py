from django.contrib import admin
from .models import TimeSheet,UserProgress,PermissionRequest,LeaveRequest,Attendance# Import your models

# Register models to Django Admin
admin.site.register(TimeSheet)
admin.site.register(UserProgress)
admin.site.register(PermissionRequest)
admin.site.register(LeaveRequest)
admin.site.register(Attendance)

