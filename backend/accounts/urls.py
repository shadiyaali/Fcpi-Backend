from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('verifyOtp/', VerifyOtp.as_view(), name='verify_otp'),
    path('resendOtp/', ResendOtp.as_view(), name='resend-otp'),
    # path('login/', LoginView.as_view(), name='login'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('add_user/', AddUser.as_view(), name='add_user'),
    path('user-roles/', UserRoleListView.as_view(), name='user_roles_list'),
    path('create-roles/', UserRoleCreateView.as_view(), name='create_roles_create'),
    path('userlist/', UserListView.as_view(), name='user-list'),
    path('useralllist/', UserAllListView.as_view(), name='user-list'),
    path('userprofile/', UserProfileCreateView.as_view(), name='user_profile'),
    path('userprofilelist/',  UserprofileListView.as_view(), name='user_profile_list'),
    path('user/<int:pk>/update/', updateUser.as_view(), name='user-update'),
    path('user/<int:pk>/delete/', DeleteUser.as_view(), name='user-delete'),
    path('singleuser/', UserProfileView.as_view(), name='user-profile'),
    path('feedback/', FeedbackCreateView.as_view(), name='feedback-create'), 
    path('ecertificate/', CertificateView.as_view(), name='certificate-view'),
    path('usercertificate/', AuthenticatedUserView.as_view(), name='authenticated-user'),
    path('user/<int:user_id>/', UserProfileAPIView.as_view(), name='user_profile_api'),
    path('enroll/<slug:slug>/', EnrollEvent.as_view(), name='enroll_event'),
    path('check-enrollment/<slug:slug>/', CheckEnrollmentView.as_view(), name='check_enrollment'),
    path('users/enrolled-events/', UserEnrolledEventListView.as_view(), name='user_enrolled_events'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change_password'),
    path('event-points/', EventPointsAPIView.as_view(), name='event_points'),
    path('singleuser/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('user/userprofile/<int:user_id>/',UserProfileUpdateView.as_view(), name='user-profile-update'),
    path('user-delete/<int:user_id>/', UserDeleteView.as_view(), name='user-delete'),
    path('user-status/<int:user_id>/', UpdateUserStatusView.as_view(), name='update-user-status'),
    path('save-csv-data/', SaveCsvDataView.as_view(), name='save_csv_data'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('verify-forgot-password-otp/', VerifyForgotPasswordOtpView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('contact/', ContactMessageAPIView.as_view(), name='contact-message'),
    path('events/<slug:slug>/enrollment-count/', EnrolledUserCountView.as_view(), name='event-enrollment-count'),
    path('usersall/', UserALLListView.as_view(), name='user-list'),
    path('user-countweek/', UserCountView.as_view(), name='user-count'),
   

]