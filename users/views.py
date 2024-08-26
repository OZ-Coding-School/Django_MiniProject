from django.core import signing
from django.core.mail import send_mail
from django.core.signing import TimestampSigner, SignatureExpired
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from users.serializers import SignupSerializer, LoginSerializer

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

        self.verify_link = self.request.build_absolute_uri(
            f"/users/verify/?code={signer_dump}"
        )
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
    code = request.GET.get('code', '')

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
        email = request.data.get('email')
        password = request.data.get('password')
        serializer = LoginSerializer(data={"email": email, "password": password}, context={'request': request})

        if serializer.is_valid():
            user = authenticate(
                request, email=serializer.data['email'], password=serializer.data['password']
            )
            if user is None:
                return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            refresh = RefreshToken.for_user(user)
            response = Response({"detail": "Login successful"}, status.HTTP_200_OK)
            response.set_cookie('access', str(refresh))
            response.set_cookie('refresh', str(refresh.access_token))
            return response
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class JWTLogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        response.data = {"detail": "Logout successful"}
        response.status_code = status.HTTP_200_OK
        return response
