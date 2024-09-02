import random

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Account


class AccountModelTestCases(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword1234",
            nickname="testuser",
            name="홍길동",
            phone="010-1111-2222",
        )
        self.account_data = {
            "user_id": self.user.id,
            "account_num": "3333-54-1231231",
            "bank_code": "090",
            "balance": 1000000,
            "type": "입출금통장",
        }

    def test_create_account(self):
        account = Account.objects.create(**self.account_data)

        self.assertEqual(account.user_id, self.user.id)
        self.assertEqual(account.account_num, self.account_data["account_num"])
        self.assertEqual(account.bank_code, self.account_data["bank_code"])
        self.assertEqual(account.balance, self.account_data["balance"])
        self.assertEqual(account.type, self.account_data["type"])

    def test_update_account_balance(self):
        account = Account.objects.create(**self.account_data)
        self.assertEqual(account.balance, self.account_data["balance"])
        account.balance = 2000000

        account.save()

        account.refresh_from_db()
        self.assertEqual(account.balance, 2000000)

    def test_delete_account(self):
        account = Account.objects.create(**self.account_data)
        self.assertEqual(Account.objects.count(), 1)

        account.delete()

        self.assertFalse(Account.objects.filter(id=account.id).exists())
        self.assertEqual(Account.objects.count(), 0)

    def test_delete_account_when_user_deleted(self):
        account = Account.objects.create(**self.account_data)
        self.assertEqual(Account.objects.count(), 1)

        self.user.delete()

        self.assertFalse(Account.objects.filter(id=account.id).exists())
        self.assertEqual(Account.objects.count(), 0)

    def test_account_str_representation(self):
        account = Account.objects.create(**self.account_data)

        self.assertEqual(str(account), f"{account.get_bank_code_display()}: {account.account_num[-4:]}")

    def test_account_masking_account_num(self):
        account = Account.objects.create(**self.account_data)

        self.assertEqual(account.masking_account_num(), "3333-54-*******")


class AccountViewTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword1234",
            nickname="testuser",
            name="홍길동",
            phone="010-1111-2222",
            is_active=True,
        )
        self.access_token = str(RefreshToken.for_user(self.user).access_token)

    def test_account_create_view(self):
        url = reverse("account-create")
        data = {
            "account_num": "3333-54-1231231",
            "bank_code": "090",
            "balance": 1000000,
            "type": "입출금",
        }

        response = self.client.post(url, data, headers={"Authorization": f"Bearer {self.access_token}"})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(response.data["user"], self.user.id)
        self.assertEqual(response.data["account_num"], data["account_num"])
        self.assertEqual(response.data["bank_code"], data["bank_code"])
        self.assertEqual(response.data["balance"], data["balance"])
        self.assertEqual(response.data["type"], data["type"])

    def test_account_list_view(self):
        for i in range(5):
            Account.objects.create(
                user_id=self.user.id,
                account_num=f"3333-54-123123{i}",
                bank_code="090",
                balance=random.randint(100000, 999999999),
                type="입출금",
            )
        url = reverse("account-list")

        response = self.client.get(url, headers={"Authorization": f"Bearer {self.access_token}"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Account.objects.count(), 5)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data[0]["user"], self.user.id)
        self.assertEqual(response.data[0]["account_num"], "3333-54-1231230")
        self.assertEqual(response.data[1]["account_num"], "3333-54-1231231")
        self.assertEqual(response.data[2]["account_num"], "3333-54-1231232")
        self.assertEqual(response.data[3]["account_num"], "3333-54-1231233")
        self.assertEqual(response.data[4]["account_num"], "3333-54-1231234")

    def test_account_detail_view(self):
        account = Account.objects.create(
            user_id=self.user.id,
            account_num="3333-54-1231231",
            bank_code="090",
            balance=1000000,
            type="입출금",
        )
        url = reverse("account-detail", kwargs={"pk": account.id})

        response = self.client.get(url, headers={"Authorization": f"Bearer {self.access_token}"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"], account.user_id)
        self.assertEqual(response.data["account_num"], account.account_num)
        self.assertEqual(response.data["bank_code"], account.bank_code)
        self.assertEqual(response.data["balance"], account.balance)
        self.assertEqual(response.data["type"], account.type)
        self.assertEqual(len(response.data["transactions"]), account.transactions.count())

    def test_account_update_view(self):
        account = Account.objects.create(
            user_id=self.user.id,
            account_num="3333-54-1231231",
            bank_code="090",
            balance=1000000,
            type="입출금",
        )
        url = reverse("account-detail", kwargs={"pk": account.id})
        data = {
            "balance": 2000000,
        }

        response = self.client.patch(url, data, headers={"Authorization": f"Bearer {self.access_token}"})

        self.assertEqual(response.status_code, 200)
        account.refresh_from_db()
        self.assertEqual(response.data["balance"], account.balance)

    def test_account_delete_view(self):
        account = Account.objects.create(
            user_id=self.user.id,
            account_num="3333-54-1231231",
            bank_code="090",
            balance=1000000,
            type="입출금",
        )
        url = reverse("account-delete", kwargs={"pk": account.id})

        response = self.client.delete(url, headers={"Authorization": f"Bearer {self.access_token}"})

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Account.objects.filter(id=account.id).exists())
