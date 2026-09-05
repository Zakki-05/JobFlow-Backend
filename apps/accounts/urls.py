from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, CurrentUserProfileView, HealthCheckView, CustomTokenObtainPairView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', CurrentUserProfileView.as_view(), name='user_profile'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
]
