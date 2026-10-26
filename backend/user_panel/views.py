from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.timezone import now
from django.http import JsonResponse
from .models import TimeSheet,UserProgress,LeaveRequest, PermissionRequest,Attendance
from .serializers import TimeSheetSerializer,UserProgressSerializer,LeaveRequestSerializer, PermissionRequestSerializer,AttendanceSerializer
from django.utils import timezone
from rest_framework import status, generics,permissions

class ClockInView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("User:", request.user)  # Debug: Print user information

        # ✅ Allow multiple clock-ins (no need to check existing timesheet)
        timesheet = TimeSheet.objects.create(user=request.user, clock_in_time=timezone.now())

        return JsonResponse({
            "message": "Clock-in successful",
            "clock_in_time": timesheet.clock_in_time.strftime("%Y-%m-%d %H:%M:%S")  # Format datetime
        })




class StartBreakView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        timesheet = TimeSheet.objects.filter(user=user, clock_out_time__isnull=True).first()
        
        if not timesheet:
            return Response({"error": "You must clock in first"}, status=400)
        
        if timesheet.break_start_time:
            return Response({"error": "Already on a break"}, status=400)

        timesheet.break_start_time = now()
        timesheet.save()
        return Response({"message": "Break started"})

class EndBreakView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        timesheet = TimeSheet.objects.filter(user=user, clock_out_time__isnull=True).first()
        
        if not timesheet or not timesheet.break_start_time:
            return Response({"error": "No active break"}, status=400)

        break_duration = now() - timesheet.break_start_time
        timesheet.total_break_time += break_duration
        timesheet.break_start_time = None
        timesheet.save()
        return Response({"message": "Break ended"})



class ClockOutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        timesheet = TimeSheet.objects.filter(user=user, clock_out_time__isnull=True).first()

        if not timesheet:
            return Response({"error": "You must clock in first"}, status=400)

        # Update clock-out time and calculate total work hours
        timesheet.clock_out_time = now()
        total_hours = timesheet.calculate_total_work_time()
        timesheet.total_work_time = total_hours
        timesheet.save()

        # Determine attendance status
        if total_hours.total_seconds() / 3600 >= 8: 
            status = "Full Day"
        elif total_hours.total_seconds() / 3600 >= 4: 
            status = "Half Day"
        else:
            status = "Absent"

        # Save attendance record
        Attendance.objects.create(
            employee=user,
            date=timesheet.clock_in_time.date(),
            clock_in=timesheet.clock_in_time,
            clock_out=timesheet.clock_out_time,
            total_hours=total_hours,
            attendance_status=status
        )

        return Response(TimeSheetSerializer(timesheet).data)



class PublishProgressView(generics.CreateAPIView):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        tasks = request.data.get('tasks', [])
        date = request.data.get('date', now().date())  # Default to today if not provided

        if not tasks:
            return Response({'error': 'No tasks provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if an entry for this user and date already exists
        if UserProgress.objects.filter(user=user, date=date).exists():
            return Response({'error': 'Progress for today has already been submitted'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new entry since none exists for today
        progress_entry = UserProgress.objects.create(user=user, date=date, tasks=tasks)

        return Response(
            {'message': 'Tasks recorded successfully', 'data': progress_entry.tasks},
            status=status.HTTP_201_CREATED
        )




class LeaveRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leaves = LeaveRequest.objects.filter(user=request.user)
        serializer = LeaveRequestSerializer(leaves, many=True)
        return Response(serializer.data)

    def post(self, request):
        print("Received Data:", request.data)  # Debugging
        serializer = LeaveRequestSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            print("Validated Data:", serializer.validated_data)  # Debugging
            serializer.save()
            print("Saved Successfully!")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print("Errors:", serializer.errors)  # Debugging
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PERMISSION REQUEST VIEWS
class PermissionRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    print("haiiiii")
    def get(self, request):
        print("helloooo")
        permissions = PermissionRequest.objects.filter(user=request.user)
        serializer = PermissionRequestSerializer(permissions, many=True)
        return Response(serializer.data)

    def post(self, request):
        print("Received Data:", request.data)  # Debugging print
        print("User:", request.user)

        data = request.data.copy()  
        data["user"] = request.user.id  # Assign the logged-in user's ID

        serializer = PermissionRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Assign user explicitly
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print("Errors:", serializer.errors)  # Print validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, date):
        """Fetch progress data for a specific user and date."""
        progress = UserProgress.objects.filter(user_id=user_id, date=date)
        serializer = UserProgressSerializer(progress, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

     

class AttendanceListCreateView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Attendance.objects.filter(employee=user)

        month = self.request.query_params.get("month")
        if month:
            year, month = map(int, month.split("-"))
            queryset = queryset.filter(
                date__year=year,
                date__month=month
            )
        return queryset

class AttendanceUpdateView(generics.UpdateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
 
 
from rest_framework.generics import ListAPIView   
class AdminAttendanceView(ListAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminUser] 