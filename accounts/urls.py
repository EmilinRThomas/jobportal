from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignupView, LoginView,VerifyOtpView,MeProfileView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='api-signup'),
    path('login/', LoginView.as_view(), name='api-login'),
    path("verify-otp/",VerifyOtpView.as_view(), name="api-verify-otp"), 
    path("profile/",MeProfileView.as_view(), name="api-profile"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
