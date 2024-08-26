from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from users import views as user_views


urlpatterns = [
    path('signup/', user_views.SignupView.as_view(), name='signup'),
    path('login/', user_views.JWTLoginView.as_view(), name='login'),
    path('logout/', user_views.JWTLogoutView.as_view(), name='logout'),
    path('verify/', user_views.verify_email, name='verify'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
]
