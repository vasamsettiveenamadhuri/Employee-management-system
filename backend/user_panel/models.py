# from django.db import models
# from django.conf import settings 
# from django.utils.timezone import now
# from django.contrib.auth import get_user_model
# from datetime import timedelta


# User=get_user_model()
# class TimeSheet(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)  
#     date = models.DateField(default=now)  
#     clock_in_time = models.DateTimeField(null=True, blank=True)
#     clock_out_time = models.DateTimeField(null=True, blank=True)
#     break_start_time = models.DateTimeField(null=True, blank=True)
#     break_end_time = models.DateTimeField(null=True, blank=True)
#     total_break_time = models.DurationField(default=timedelta())  
#     total_work_time = models.DurationField(default=timedelta())  

#     def __str__(self):
#         return f"{self.user.username} - {self.date}"

#     def calculate_total_work_time(self):
#         if self.clock_in_time and self.clock_out_time:
#             total_time = self.clock_out_time - self.clock_in_time
#             return total_time - self.total_break_time  
#         return timedelta()


from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now

User = get_user_model()

class TimeSheet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clock_in_time = models.DateTimeField(default=timezone.now)
    clock_out_time = models.DateTimeField(null=True, blank=True)
    break_start_time = models.DateTimeField(null=True, blank=True)
    total_break_time = models.DurationField(default=timedelta())  
    total_work_time = models.DurationField(null=True, blank=True)

    def calculate_total_work_time(self):
        if self.clock_out_time:
            work_duration = self.clock_out_time - self.clock_in_time
            return work_duration - self.total_break_time
        return None

    def __str__(self):
        return f"{self.user.username} - {self.clock_in_time.date()}"


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=now)  # Keep date for grouping
    tasks = models.JSONField(default=list)  # ✅ Store tasks in JSON format

    def __str__(self):
        return f"{self.user.username} - {self.date}"



class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    LEAVE_MODES = [
        ('full_day', 'Full Day'),
        ('half_day', 'Half Day'),
    ]

    LEAVE_TYPES = [
        ('sick_leave', 'Sick Leave'),
        ('casual_leave', 'Casual Leave'),
        ('earned_leave', 'Earned Leave'),
        ('maternity_leave', 'Maternity Leave'),
        ('paternity_leave', 'Paternity Leave'),
        ('unpaid_leave', 'Unpaid Leave'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(default=timezone.localdate)
    is_half_day = models.BooleanField(default=False)
    leave_mode = models.CharField(max_length=10, choices=LEAVE_MODES, default='full_day')
    date_of_attending_office = models.DateField(default=timezone.localdate)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, default='casual_leave')
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def is_approved(self):
        return self.status == "approved"

    def is_rejected(self):
        return self.status == "rejected"

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} ({self.status})"

    


class PermissionRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    ABSENCE_TYPES = [
        ('short_break', 'Short Break'),
        ('half_day', 'Half Day Permission'),
        ('full_day', 'Full Day Permission'),
        ('emergency_leave', 'Emergency Leave'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission_start_date = models.DateField(default=timezone.localdate)
    permission_end_date = models.DateField(default=timezone.localdate)
    absence_type = models.CharField(max_length=20, choices=ABSENCE_TYPES, default='short_break')
    compensation_start = models.DateField(default=timezone.localdate)
    compensation_end = models.DateField(default=timezone.localdate)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def is_approved(self):
        return self.status == "approved"

    def is_rejected(self):
        return self.status == "rejected"

    def __str__(self):
        return f"{self.user.username} - {self.absence_type} ({self.status})"


from django.db import models
from datetime import timedelta

class Attendance(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    clock_in = models.TimeField(null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)
    total_hours = models.FloatField(default=0, editable=False)
    attendance_status = models.CharField(max_length=10, default="Absent", editable=False)

    def save(self, *args, **kwargs):
        if self.clock_in and self.clock_out:
            # Convert time fields to timedelta
            clock_in_time = timedelta(
                hours=self.clock_in.hour, minutes=self.clock_in.minute, seconds=self.clock_in.second
            )
            clock_out_time = timedelta(
                hours=self.clock_out.hour, minutes=self.clock_out.minute, seconds=self.clock_out.second
            )

            # Calculate total hours worked
            self.total_hours = (clock_out_time - clock_in_time).total_seconds() / 3600

            # Update attendance status
            if self.total_hours >= 8:
                self.attendance_status = "Full Day"
            elif self.total_hours >= 4:
                self.attendance_status = "Half Day"
            else:
                self.attendance_status = "Absent"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.username} - {self.date} - {self.attendance_status}"
