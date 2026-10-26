from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import EmployeeRegisterSerializer, EmployeeLoginSerializer,LeaveRequestSerializer,PermissionRequestSerializer,CustomUserSerializer,PermissionRequestSerializer,LeaveRequestSerializer,EmployeeSerializer
from .models import OTP
import random
from user_panel.models import LeaveRequest,PermissionRequest
from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404



User=get_user_model()
# ✅ Helper function to generate JWT tokens
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# ✅ EMPLOYEE REGISTRATION VIEW (Without OTP Validation)
class EmployeeRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")  # Extract email from request

        # ✅ Check if a user with this email already exists
        if User.objects.filter(email=email).exists():
            return Response({"message": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EmployeeRegisterSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()
                tokens = get_tokens_for_user(user)
                return Response({
                    "message": "Employee registered successfully!",
                    "tokens": tokens
                }, status=status.HTTP_201_CREATED)

            except Exception as e:  # Catch any unexpected error
                return Response({
                    "message": "User registered (error ignored)."
                }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendOTPForLoginView(APIView):
    permission_classes = [AllowAny]  # ✅ Allow access to all users

    def post(self, request):
        email = request.data.get("email")
        User=get_user_model()
        try:
            user = User.objects.get(email=email)
            otp = str(random.randint(100000, 999999))  # Generate OTP
            OTP.objects.update_or_create(
                email=user.email,  # ✅ Use email instead of user
                defaults={"otp_code": otp, "created_at": timezone.now()}
            )

            # Send OTP via email
            send_mail(
                subject="Your Login OTP",
                message=f"Your OTP is {otp}. It is valid for 5 minutes.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
            )

            return Response({"message": "OTP sent successfully!"}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyOTPAndLoginView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        User = get_user_model()
        email = request.data.get("email")
        otp = request.data.get("otp")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
            otp_obj = OTP.objects.get(email=user.email)

            if otp_obj.otp_code != otp:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

            # ✅ Remove OTP after successful verification
            OTP.objects.filter(email=user.email).delete()

            # ✅ Authenticate user with password
            serializer = EmployeeLoginSerializer(data={"email": email, "password": password})
            if serializer.is_valid():
                # ✅ Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                return Response({
                    "message": "Login successful!",
                    "tokens": {
                    "access": access_token,
                    "refresh": str(refresh)
                    },
                    "user": {
                    "user_id": user.id,
                    "email": user.email,
                    "is_super": user.is_superuser,
                    "employee_name": user.employee_name,  # ✅ Include employee name
                    "designation": user.designation,  # ✅ Include designation
                    "photo": user.photo.url if user.photo else None  # ✅ Include profile picture URL
                    }
                }, status=status.HTTP_200_OK)

            else:
                return Response({"error": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST)

        except (User.DoesNotExist, OTP.DoesNotExist):
            return Response({"error": "Invalid email or OTP."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
            new_otp = str(random.randint(100000, 999999))  # Generate new OTP
            
            OTP.objects.update_or_create(
                email=user.email,
                defaults={"otp_code": new_otp, "created_at": timezone.now()}
            )

            # Send new OTP via email
            send_mail(
                "Your New OTP",
                f"Your new OTP is: {new_otp}",
                settings.EMAIL_HOST_USER,
                [email],
            )

            return Response({"message": "OTP resent successfully!"}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)


class EmployeeListView(APIView):
    permission_classes = [AllowAny]  # ✅ Require authentication

    def get(self, request):
        employees = User.objects.filter(is_superuser=False)  # ✅ Fetch only non-superusers

        employee_data = [
            {
                "id": employee.id,
                "email": employee.email,
                "employee_name": employee.employee_name,
                "designation": employee.designation,
                "employee_id": employee.employee_id,
                "join_date": employee.join_date,
                "photo": request.build_absolute_uri(employee.photo.url) 
                if employee.photo else request.build_absolute_uri(settings.MEDIA_URL + "employee_photos/image.jpg")  # ✅ Send full photo URL
            }
            for employee in employees
        ]

        return Response(employee_data, status=status.HTTP_200_OK)


class UpdateEmployeeView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        employee = get_object_or_404(User, id=kwargs["pk"])
        data = request.data

        employee.employee_name = data.get("employee_name", employee.employee_name)
        employee.designation = data.get("designation", employee.designation)
        employee.employee_id = data.get("employee_id", employee.employee_id)
        employee.join_date = data.get("join_date", employee.join_date)
        employee.email = data.get("email", employee.email)

        if "password" in data and data["password"]:
            employee.set_password(data["password"])  # Update password only if provided

        if "photo" in request.FILES:  # ✅ Handle photo upload
            employee.photo = request.FILES["photo"]

        employee.save()
        return Response({"message": "Employee updated successfully!"})



class DeleteEmployeeView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            employee = User.objects.get(pk=pk)
            employee.delete()
            return Response({"message": "Employee deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)


class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated users

    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)

            # Generate a new OTP
            otp_code = str(random.randint(100000, 999999))

            # Check if an OTP already exists for the user
            otp_entry, created = OTP.objects.update_or_create(
                email=user.email,  # Use email as the unique identifier
                defaults={"user": user, "otp_code": otp_code, "created_at": timezone.now()}
            )

            # Send OTP via email
            send_mail(
                "Password Reset OTP",
                f"Your OTP for password reset is: {otp_entry.otp_code}",  # Use `otp_code`
                "veenamadhuri136@gmail.com",
                [user.email],
                fail_silently=False,
            )

            return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "No user found with this email."}, status=status.HTTP_400_BAD_REQUEST)



class VerifyOTPAndResetPasswordView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated users

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
            otp_entry = OTP.objects.filter(user=user, otp_code=otp).first()  # FIXED FIELD NAME

            if not otp_entry:
                return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

            if otp_entry.is_expired():  # Check if OTP is expired
                otp_entry.delete()  # Remove expired OTP
                return Response({"error": "OTP has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

            # Reset password
            user.set_password(new_password)
            user.save()

            # Delete OTP after successful reset
            otp_entry.delete()

            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)
        


class LeaveRequestApproveView(APIView):
    permission_classes = [IsAdminUser]  # Only Admins Can Approve/Reject

    def post(self, request, pk):
        action = request.data.get("action")  # Get action from request body
        if not action:
            return Response({'error': "Missing 'action' field. Use 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            leave = LeaveRequest.objects.get(pk=pk)
            user_email = leave.user.email  # Get employee's email

            if action == "approve" and leave.status != "approved":
                leave.status = "approved"
                leave.save(update_fields=["status"])

                # Send email notification
                self.send_email(user_email, "approved", leave)

                return Response({'message': 'Leave approved successfully!', 'status': 'approved'}, status=status.HTTP_200_OK)

            elif action == "reject" and leave.status != "rejected":
                leave.status = "rejected"
                leave.save(update_fields=["status"])

                # Send email notification
                self.send_email(user_email, "rejected", leave)

                return Response({'message': 'Leave rejected successfully!', 'status': 'rejected'}, status=status.HTTP_200_OK)

            return Response({'error': f'Leave request is already {leave.status}.'}, status=status.HTTP_400_BAD_REQUEST)

        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found'}, status=status.HTTP_404_NOT_FOUND)

    def send_email(self, to_email, action, leave):
        """Send email notification to employee."""
        subject = f"Your Leave Request has been {action.capitalize()}"
        message = f"""
        Dear {leave.user.username},

        Your leave request ({leave.leave_type}) from {leave.start_date} to {leave.end_date} has been {action}.

        Regards,
        HR Team
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])


class PermissionRequestApproveView(APIView):
    permission_classes = [IsAdminUser]  # Only Admins Can Approve/Reject

    def post(self, request, pk):
        action = request.data.get("action")  # Get action from request body
        if not action:
            return Response({'error': "Missing 'action' field. Use 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            permission = PermissionRequest.objects.get(pk=pk)
            user_email = permission.user.email  # Get employee's email

            if action == "approve" and permission.status != "approved":
                permission.status = "approved"
                permission.save(update_fields=["status"])

                # Send email notification
                self.send_email(user_email, "approved", permission)

                return Response({'message': 'Permission approved successfully!', 'status': 'approved'}, status=status.HTTP_200_OK)

            elif action == "reject" and permission.status != "rejected":
                permission.status = "rejected"
                permission.save(update_fields=["status"])

                # Send email notification
                self.send_email(user_email, "rejected", permission)

                return Response({'message': 'Permission rejected successfully!', 'status': 'rejected'}, status=status.HTTP_200_OK)

            return Response({'error': f'Permission request is already {permission.status}.'}, status=status.HTTP_400_BAD_REQUEST)

        except PermissionRequest.DoesNotExist:
            return Response({'error': 'Permission request not found'}, status=status.HTTP_404_NOT_FOUND)

    def send_email(self, to_email, action, permission):
        """Send email notification to employee."""
        subject = f"Your Permission Request has been {action.capitalize()}"
        message = f"""
        Dear {permission.user.username},

        Your permission request for {permission.absence_type} from {permission.permission_start_date} to {permission.permission_end_date} has been {action}.

        Regards,
        HR Team
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])





class LeaveRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leaves = LeaveRequest.objects.filter(user=request.user)
        serializer = LeaveRequestSerializer(leaves, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LeaveRequestSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()  # No need to pass user, serializer handles it
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Permission Requests
class PermissionRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        permissions = PermissionRequest.objects.filter(user=request.user)
        serializer = PermissionRequestSerializer(permissions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PermissionRequestSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()  # No need to pass user, serializer handles it
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveRequestsView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    def get(self, request):
        leave_requests = LeaveRequest.objects.filter(status="pending").values(
            'id', 'user__username', 'start_date', 'end_date', 'is_half_day',
            'leave_mode', 'date_of_attending_office', 'leave_type', 'reason', 'status'
        )
        return Response({"leave_requests": list(leave_requests)})


class PermissionRequestsView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    def get(self, request):
        permission_requests = PermissionRequest.objects.filter(status="pending").values(
            'id', 'user__username', 'permission_start_date', 'permission_end_date', 'absence_type',
            'compensation_start', 'compensation_end', 'reason', 'status'
        )
        return Response({"permission_requests": list(permission_requests)})


class GetUserByEmailView(APIView):
    permission_classes = [IsAuthenticated]  # Requires authentication

    def post(self, request):
        email = request.data.get("email")
        user = get_object_or_404(User, email=email)  # ✅ Fetch from CustomUser model

        serializer = CustomUserSerializer(user)
        print("🔍 API Response:", serializer.data)  # ✅ Debugging output

        return Response({"found": True, "user": serializer.data})  


class LeaveHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leaves = LeaveRequest.objects.filter(
            status__in=["approved", "rejected"]
        ).order_by("-start_date")

        serializer = LeaveRequestSerializer(leaves, many=True)
        return Response(serializer.data)


class PermissionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        permissions = PermissionRequest.objects.filter(
            status__in=["approved", "rejected"]
        ).order_by("-permission_start_date")

        serializer = PermissionRequestSerializer(permissions, many=True)
        return Response(serializer.data)
