from django.urls import path
from .views import SignupView, LoginView,VerifyOtpView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='api-signup'),
    path('login/', LoginView.as_view(), name='api-login'),
    path("verify-otp/",VerifyOtpView.as_view(), name="api-verify-otp"), 
]
