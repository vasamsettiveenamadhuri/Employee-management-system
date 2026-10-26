from django.urls import path
from .views import EmployeeRegisterView, VerifyOTPAndLoginView,SendOTPForLoginView,EmployeeListView,EmployeeListView,UpdateEmployeeView,DeleteEmployeeView,RequestPasswordResetView,VerifyOTPAndResetPasswordView,PermissionRequestApproveView,LeaveRequestApproveView,LeaveRequestsView,PermissionRequestsView,GetUserByEmailView,ResendOTPView,PermissionHistoryView,LeaveHistoryView
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


urlpatterns = [
    path('register/', EmployeeRegisterView.as_view(), name='employee-register'),
    path('login/', VerifyOTPAndLoginView.as_view(), name='employee-login'),
    path('emplist/',EmployeeListView.as_view(),name='emplist'),
    path("send-otp-login/", SendOTPForLoginView.as_view(), name="send-otp-login"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("update/<int:pk>/", UpdateEmployeeView.as_view(), name="update_employee"),
    path("delete/<int:pk>/", DeleteEmployeeView.as_view(), name="delete_employee"),
    path("password-reset-otp/", RequestPasswordResetView.as_view(), name="request-password-reset"),
    path("reset-password-otp/", VerifyOTPAndResetPasswordView.as_view(), name="verify-otp-reset-password"),
    path('permission/<int:pk>/approve/', PermissionRequestApproveView.as_view(), name='permission-approve'),
    path('leave/<int:pk>/approve/', LeaveRequestApproveView.as_view(), name='leave-approve'),
     path('leave_requests/', LeaveRequestsView.as_view(), name='leave_requests'),
    path('permission_requests/', PermissionRequestsView.as_view(), name='permission_requests'),
    path("get-user/", GetUserByEmailView.as_view(), name="get-user"),
     path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
      path("history/permissions/", PermissionHistoryView.as_view(), name="permission-history"),
    path("history/leaves/", LeaveHistoryView.as_view(), name="leave-history"),
]