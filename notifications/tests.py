from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from analysis.models import Analysis
from notifications.models import Notification


class SignalTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword1234",
            nickname="testuser",
            name="홍길동",
            phone="010-1111-2222",
            is_active=True,
        )

    def test_create_notification_when_analysis_created(self):
        Analysis.objects.create(
            user=self.user,
            about="TOTAL_SPENDING",
            type='WEEKLY',
            period_start=datetime.today(),
            period_end=datetime.today() + timedelta(days=1),
            description="test Analysis",
            created_at=datetime.today(),
            updated_at=datetime.today(),
        )

        self.assertEqual(Analysis.objects.filter(user=self.user).count(), 1)
        self.assertTrue(Notification.objects.filter(user=self.user).exists())

    def test_create_notification_when_analysis_updated(self):
        analysis = Analysis.objects.create(
            user=self.user,
            about="TOTAL_SPENDING",
            type='WEEKLY',
            period_start=datetime.today(),
            period_end=datetime.today() + timedelta(days=1),
            description="test Analysis",
            created_at=datetime.today(),
            updated_at=datetime.today(),
        )

        # 업데이트 시도
        analysis.description = "updated Analysis"
        analysis.save()

        # 수정 후 알림이 있는지 확인
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 2)
        self.assertTrue(Notification.objects.filter(user=self.user, message__contains="수정된").exists())


class NotificationAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword1234",
            nickname="testuser",
            name="홍길동",
            phone="010-1111-2222",
            is_active=True,
        )
        self.access = str(RefreshToken.for_user(self.user).access_token)

        self.notification = Notification.objects.create(
            user=self.user,
            message="test notification",
        )

    def test_notification_list_view(self):
        response = self.client.get(reverse("notification-list"), headers={"Authorization": f"Bearer {self.access}"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["message"], "test notification")

    def test_notification_read_view(self):
        response = self.client.patch(
            reverse("notification-read", kwargs={"pk": self.notification.pk}),
            headers={"Authorization": f"Bearer {self.access}"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "test notification")
        self.assertTrue(response.data["is_read"])
