from django.urls import path
from .views import (LoginView, UserListView, RegisterView,
                    ForgotPassword, EmailVerifyAPIView, UserGetAPIView, ChangeUserStatus, DeleteUserAPIView)

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('users/', UserListView.as_view()),
    path('register/', RegisterView.as_view()),
    path('edit-user/', ForgotPassword.as_view()),
    path('email-verify/<str:token>', EmailVerifyAPIView.as_view()),
    path('user-info/', UserGetAPIView.as_view()),
    path('update-user/<int:pk>', ChangeUserStatus.as_view()),
    path('delete-user/<int:pk>', DeleteUserAPIView.as_view()),
]
