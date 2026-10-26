from django.urls import path
from .views import ClockInView, StartBreakView, EndBreakView, ClockOutView,PublishProgressView,LeaveRequestListCreateView,PermissionRequestListCreateView,UserProgressView,AttendanceListCreateView,AttendanceUpdateView,AdminAttendanceView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('clock_in/', ClockInView.as_view(), name='clock_in'),
    path('start_break/', StartBreakView.as_view(), name='start_break'),
    path('end_break/', EndBreakView.as_view(), name='end_break'),
    path('clock_out/', ClockOutView.as_view(), name='clock_out'),
    path('publish/', PublishProgressView.as_view(), name="publish_tasks"),


    path('leave/', LeaveRequestListCreateView.as_view(), name='leave-list-create'),

    # Permission Requests
    path('permission/', PermissionRequestListCreateView.as_view(), name='permission-list-create'),

    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('user-progress/<int:user_id>/<str:date>/', UserProgressView.as_view(), name='user-progress'),
    path('attendance/', AttendanceListCreateView.as_view(), name='attendance-list'),
    path('attendance/<int:pk>/', AttendanceUpdateView.as_view(), name='attendance-update'),
     path('admin-attendance/', AdminAttendanceView.as_view(), name='admin-attendance'),
]
