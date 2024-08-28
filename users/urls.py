from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users import views as user_views

urlpatterns = [
    path("signup/", user_views.SignupView.as_view(), name="signup"),
    path("login/", user_views.JWTLoginView.as_view(), name="login"),
    path("logout/", user_views.JWTLogoutView.as_view(), name="logout"),
    path("verify/", user_views.verify_email, name="verify"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    # kakao_oauth
    path("oauth/kakao/login/", user_views.KakaoLoginView.as_view(), name="kakao_login"),
    path("oauth/kakao/callback/", user_views.KakaoCallbackView.as_view(), name="kakao_callback"),
    # google_oauth
    path("oauth/google/login/", user_views.GoogleLoginView.as_view(), name="google_login"),
    path("oauth/google/callback/", user_views.GoogleCallbackView.as_view(), name="google_callback"),
    # naver_oauth
    path("oauth/naver/login/", user_views.NaverLoginView.as_view(), name="naver_login"),
    path("oauth/naver/callback/", user_views.NaverCallbackView.as_view(), name="naver_callback"),
]
