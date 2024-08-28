from abc import abstractmethod
import requests
from django.contrib.auth import authenticate, get_user_model
from django.core import signing
from django.core.mail import send_mail
from django.core.signing import SignatureExpired, TimestampSigner
from django.shortcuts import redirect
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.mixins import KaKaoProviderInfoMixin, GoogleProviderInfoMixin, NaverProviderInfoMixin
from users.serializers import LoginSerializer, SignupSerializer

User = get_user_model()


class SignupView(CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    verify_link = None

    def perform_create(self, serializer):
        user = serializer.save()
        signer = TimestampSigner()
        signed_user_email = signer.sign(user.email)
        signer_dump = signing.dumps(signed_user_email)

        self.verify_link = self.request.build_absolute_uri(f"/users/verify/?code={signer_dump}")
        subject = f"[Finance Manager]{user.email}님의 이메일 인증 링크입니다."
        message = f"""
                    아래의 링크를 클릭하여 이메일 인증을 완료해주세요.\n\n
                    {self.verify_link}
                    """
        send_mail(subject=subject, message=message, from_email=None, recipient_list=(user.email,))

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data["detail"] = "회원가입이 완료되었습니다. 이메일 인증을 완료하여 계정을 활성화 해주세요."
        response.data["verify_link"] = self.verify_link
        return response


def verify_email(request):
    code = request.GET.get("code", "")

    signer = TimestampSigner()
    try:
        decoded_user_email = signing.loads(code)
        user_email = signer.unsign(decoded_user_email, max_age=60 * 5)
    except (TypeError, SignatureExpired):
        return Response({"detail": "Invalid or expired verification code"}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, email=user_email)
    user.is_active = True
    user.save()
    return Response({"detail": "Email verification successful"}, status=status.HTTP_200_OK)


class JWTLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        serializer = LoginSerializer(data={"email": email, "password": password})

        if serializer.is_valid():
            user = authenticate(request, email=serializer.data["email"], password=serializer.data["password"])
            if user is None:
                return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            refresh = RefreshToken.for_user(user)
            response = Response({"detail": "Login successful"}, status.HTTP_200_OK)
            response.set_cookie("access", str(refresh))
            response.set_cookie("refresh", str(refresh.access_token))
            return response
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class JWTLogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        response.data = {"detail": "Logout successful"}
        response.status_code = status.HTTP_200_OK
        return response


class OAuthLoginView(APIView):
    permission_classes = [AllowAny]

    @abstractmethod
    def get_provider_info(self):
        pass

    def get(self, request, *args, **kwargs):
        provider_info = self.get_provider_info()
        params = self.get_params(provider_info=provider_info)
        return redirect(f"{provider_info["authorization_url"]}?{urlencode(params)}")

    def get_params(self, provider_info):
        params = {
            "client_id": provider_info["client_id"],
            "redirect_uri": self.get_callback_url(provider_info=provider_info),
            "response_type": "code",
        }

        additional_params = {
            "카카오": {"prompt": "login"},
            "네이버": {"state": "state"},
            "구글": {"scope": "email profile"},
        }

        params.update(additional_params.get(provider_info["name"], {}))
        return params

    def get_callback_url(self, provider_info):
        domain = self.request.scheme + '://' + self.request.META.get('HTTP_HOST', '')
        callback_url = domain + provider_info["callback_url"]
        return callback_url


class OAuthCallbackView(OAuthLoginView):
    permission_classes = [AllowAny]

    @abstractmethod
    def get_provider_info(self):
        pass

    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        if not code:
            return Response({"msg": "인가코드가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        provider_info = self.get_provider_info()
        token_response = self.get_token(code, provider_info)

        if token_response.status_code != status.HTTP_200_OK:
            return Response(
                {"msg": f"{provider_info['name']} 서버로 부터 토큰을 받아오는데 실패하였습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = token_response.json().get("access_token")
        profile_response = self.get_profile(access_token, provider_info)
        if profile_response.status_code != status.HTTP_200_OK:
            return Response(
                {"msg": f"{provider_info['name']} 서버로 부터 프로필 데이터를 받아오는데 실패하였습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self.login_process_user(request, profile_response.json(), provider_info)

    def get_token(self, code, provider_info):
        return requests.post(
            provider_info["token_url"],
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.get_callback_url(provider_info=provider_info),
                "client_id": provider_info["client_id"],
                "client_secret": provider_info.get("client_secret"),
            },
        )

    def get_profile(self, access_token, provider_info):
        return requests.get(
            provider_info["profile_url"],
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
            },
        )

    def login_process_user(self, request, profile_res_data, provider_info):
        email, nickname = self.get_user_data(provider_info, profile_res_data)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_oauth_user(email=email, nickname=nickname)

        refresh_token = RefreshToken.for_user(user)
        response_data = {
            "email": user.email,
            "nickname": user.nickname,
        }

        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie("access", str(refresh_token.access_token))
        response.set_cookie("refresh", str(refresh_token))

        return response

    def get_user_data(self, provider_info, profile_res_data):
        # 각 provider의 프로필 데이터 처리 로직
        if provider_info["name"] == "구글":
            email = profile_res_data.get(provider_info["email_field"])
            nickname = profile_res_data.get(provider_info["nickname_field"])
            return email, nickname

        elif provider_info["name"] == "네이버":
            profile_data = profile_res_data.get("response")
            email = profile_data.get(provider_info["email_field"])
            nickname = profile_data.get(provider_info["nickname_field"])
            return email, nickname

        elif provider_info["name"] == "카카오":
            account_data = profile_res_data.get("kakao_account")
            email = account_data.get(provider_info["email_field"])
            profile_data = account_data.get("profile")
            nickname = profile_data.get(provider_info["nickname_field"])
            return email, nickname


class KakaoLoginView(KaKaoProviderInfoMixin, OAuthLoginView):
    pass


class GoogleLoginView(GoogleProviderInfoMixin, OAuthLoginView):
    pass


class NaverLoginView(NaverProviderInfoMixin, OAuthLoginView):
    pass


class KakaoCallbackView(KaKaoProviderInfoMixin, OAuthCallbackView):
    pass


class GoogleCallbackView(GoogleProviderInfoMixin, OAuthCallbackView):
    pass


class NaverCallbackView(NaverProviderInfoMixin, OAuthCallbackView):
    pass

