from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTestCase(TestCase):
	def setUp(self):
		self.user_data = {
			'email': 'test@example.com',
			'password': 'testpassword1234',
			'nickname': 'testuser',
			'name': '홍길동',
			'phone': '010-1111-2222'
		}

	def test_create_user(self):
		user = User.objects.create_user(**self.user_data)

		self.assertEqual(user.email, self.user_data['email'])
		self.assertEqual(user.nickname, self.user_data['nickname'])
		self.assertTrue(user.check_password(self.user_data['password']))
		self.assertFalse(user.is_staff)
		self.assertFalse(user.is_superuser)
		self.assertFalse(user.is_active)

	def test_create_superuser(self):
		superuser = User.objects.create_superuser(**self.user_data)

		self.assertEqual(superuser.email, self.user_data['email'])
		self.assertEqual(superuser.nickname, self.user_data['nickname'])
		self.assertTrue(superuser.check_password(self.user_data['password']))
		self.assertTrue(superuser.is_staff)
		self.assertTrue(superuser.is_superuser)
		self.assertTrue(superuser.is_active)

	def test_update_user(self):
		user = User.objects.create_user(**self.user_data)

		user.nickname = 'updateduser'
		user.save()

		user.refresh_from_db()
		self.assertEqual(user.nickname, 'updateduser')

	def test_delete_user(self):
		user = User.objects.create_user(**self.user_data)
		self.assertEqual(User.objects.count(), 1)

		user.delete()

		self.assertEqual(User.objects.count(), 0)
