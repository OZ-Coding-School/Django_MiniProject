import random
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import Account
from analysis.analyzers import SpendingAnalyzer
from analysis.models import Analysis
from analysis.utils import DateUtils
from transactions.models import Transaction

User = get_user_model()
datetime_utils = DateUtils()


class SpendingAnalyzerTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword1234",
            nickname="testuser",
            name="홍길동",
            phone="010-1111-2222",
            is_active=True,
        )
        self.account = Account.objects.create(
            user_id=self.user.id, account_num="3333-54-1231231", bank_code="090", balance=1000000, type="CHECKING"
        )
        self.analyzer = SpendingAnalyzer(user_id=self.user.id)

    def test_make_matplot_weekly_spending(self):
        Transaction.objects.create(
            account_id=self.account.id,
            trans_amount=random.randint(10000, 100000),
            print_content="지난주 출금",
            trans_type="WITHDRAW",
            trans_method="AUTOMATIC_TRANSFER",
            trans_date=datetime_utils.get_last_week_start().date(),
            trans_time=datetime_utils.today.time(),
        )
        Transaction.objects.create(
            account_id=self.account.id,
            trans_amount=random.randint(10000, 100000),
            print_content="이번주 출금",
            trans_type="WITHDRAW",
            trans_method="AUTOMATIC_TRANSFER",
            trans_date=datetime_utils.get_this_week_start().date(),
            trans_time=datetime_utils.today.time(),
        )

        self.analyzer.make_matplot_weekly_spending()

        # Analysis 객체가 생성되었는지 확인
        self.assertTrue(
            Analysis.objects.filter(user=self.user, about="TOTAL_SPENDING", type="WEEKLY").exists(),
            "Weekly spending analysis was not saved in the database.",
        )

    def test_make_matplot_monthly_spending(self):
        Transaction.objects.create(
            account_id=self.account.id,
            trans_amount=random.randint(10000, 100000),
            print_content="지난달 소비",
            trans_type="WITHDRAW",
            trans_method="AUTOMATIC_TRANSFER",
            trans_date=datetime_utils.get_last_month_start().date(),
            trans_time=datetime_utils.today.time(),
        )
        Transaction.objects.create(
            account_id=self.account.id,
            trans_amount=random.randint(10000, 100000),
            print_content="이번달 소비",
            trans_type="WITHDRAW",
            trans_method="AUTOMATIC_TRANSFER",
            trans_date=datetime_utils.get_this_month_start().date(),
            trans_time=datetime_utils.today.time(),
        )

        self.analyzer.make_matplot_monthly_spending()

        # Analysis 객체가 생성되었는지 확인
        self.assertTrue(
            Analysis.objects.filter(user=self.user, about="TOTAL_SPENDING", type="MONTHLY").exists(),
            "Monthly spending analysis was not saved in the database.",
        )


class AnalysisAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword1234",
            nickname="testuser",
            name="홍길동",
            phone="010-1111-2222",
            is_active=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_get_analysis(self):
        for i in range(10):
            Analysis.objects.create(
                user=self.user,
                about="TOTAL_SPENDING",
                type="WEEKLY",
                period_start=datetime.today(),
                period_end=datetime.today() + timedelta(days=8),
                description=f"test Analysis {i + 1}",
                created_at=datetime.today(),
                updated_at=datetime.today(),
            )
        response = self.client.get(reverse("analysis"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)
        self.assertEqual(response.data[0]["description"], "test Analysis 1")
        self.assertEqual(response.data[9]["description"], "test Analysis 10")
