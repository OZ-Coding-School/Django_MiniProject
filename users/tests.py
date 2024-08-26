from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from django.urls import reverse
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "password": "testpassword1234",
            "nickname": "testuser",
            "name": "홍길동",
            "phone": "010-1111-2222",
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.nickname, self.user_data["nickname"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_active)

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(**self.user_data)

        self.assertEqual(superuser.email, self.user_data["email"])
        self.assertEqual(superuser.nickname, self.user_data["nickname"])
        self.assertTrue(superuser.check_password(self.user_data["password"]))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)

    def test_update_user(self):
        user = User.objects.create_user(**self.user_data)

        user.nickname = "updateduser"
        user.save()

        user.refresh_from_db()
        self.assertEqual(user.nickname, "updateduser")

    def test_delete_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(User.objects.count(), 1)

        user.delete()

        self.assertEqual(User.objects.count(), 0)


class UserViewTestCase(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "password": "testpassword1234",
            "nickname": "testuser",
            "name": "홍길동",
            "phone": "010-1111-2222",
        }
        self.user = User.objects.create_user(**self.user_data)
        self.user.is_active = True
        self.user.save()

        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.signup_url = reverse('signup')

    def test_user_jwt_login(self):
        response = self.client.post(
            self.login_url,
            {
                "email": self.user_data["email"],
                "password": self.user_data["password"]
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.cookies)
        self.assertIn("refresh", response.cookies)
        self.assertEqual(response.data['detail'], "Login successful")

    def test_jwt_login_failure(self):
        # 잘못된 자격 증명으로 로그인 시도
        response = self.client.post(
            self.login_url,
            {
                "email": self.user_data["email"],
                'password': 'wrongpassword'
            }
        )

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, 401)

        # 쿠키가 설정되지 않았는지 확인
        self.assertNotIn('access', response.cookies)
        self.assertNotIn('refresh', response.cookies)

        self.assertEqual(response.data['detail'], "Invalid credentials")

    def test_jwt_logout(self):
        refresh_token = RefreshToken.for_user(self.user)
        access = str(refresh_token.access_token)
        self.client.cookies["refresh"] = str(refresh_token)
        self.client.cookies["refresh"] = access

        response = self.client.post(self.logout_url, headers={'Authorization': f'Bearer {access}'})

        # 상태코드 확인
        self.assertEqual(response.status_code, 200)

        # 쿠키가 삭제되었는지 확인
        self.assertEqual(response.cookies['access'].value, "")
        self.assertEqual(response.cookies['refresh'].value, "")

        # 응답 메시지 확인
        self.assertEqual(response.data['detail'], "Logout successful")

    def test_signup(self):
        user_data = {
            "email": "newuser@example.com",
            "password": "newpassword1234",
            "nickname": "newuser",
            "name": "허균",
            "phone": "010-3333-4444",
        }

        response = self.client.post(self.signup_url, user_data)

        # 응답 데이터에 이메일 인증 링크와 메시지가 포함되었는지 확인
        self.assertEqual(response.status_code, 201)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], "회원가입이 완료되었습니다. 이메일 인증을 완료하여 계정을 활성화 해주세요.")
        self.assertIn('verify_link', response.data)

        # 이메일이 발송되었는지 확인
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(user_data['email'], mail.outbox[0].to)
        self.assertIn('이메일 인증 링크입니다', mail.outbox[0].subject)
        self.assertIn(response.data['verify_link'], mail.outbox[0].body)

        # 데이터베이스에 유저가 생성되었는지 확인
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())

    def test_signup_with_existing_email(self):
        # 이미 생성된 유저와 동일한 이메일로 회원가입 시도
        response = self.client.post(self.signup_url, self.user_data, format='json')

        # 응답 상태 코드 확인 (400 Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 오류 메시지가 올바른지 확인
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'][0], 'user의 email은/는 이미 존재합니다.')

    def test_token_refresh(self):
        refresh_token = RefreshToken.for_user(self.user)

        response = self.client.post(reverse('refresh'), data={"refresh": refresh_token})

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
