from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

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

    def test_user_jwt_login(self):
        response = self.client.post(
            "users/login/",
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
            "users/login/",
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

        # 응답 데이터 확인
        self.assertEqual(response.data['detail'], "Invalid credentials")

    def test_jwt_logout(self):
        response = self.client.post(
            "users/login/",
            {
                "email": self.user_data["email"],
                "password": self.user_data["password"]
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.cookies)
        self.assertIn("refresh", response.cookies)

        response = self.client.post("users/logout/")

        # 상태코드 확인
        self.assertEqual(response.status_code, 200)

        # 쿠키가 삭제되었는지 확인
        self.assertNotIn("access", response.cookies)
        self.assertNotIn("refresh", response.cookies)

        # 응답 메시지 확인
        self.assertEqual(response.data['detail'], "Logout successful")