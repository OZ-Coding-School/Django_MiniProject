import random
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Account
from transactions.models import Transaction


class TransactionTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword1234",
            nickname="testuser",
            name="홍길동",
            phone="010-1111-2222",
        )
        self.account = Account.objects.create(
            user_id=self.user.id, account_num="3333-54-1231231", bank_code="090", balance=1000000, type="입출금통장"
        )
        self.transaction_data = {
            "account_id": self.account.id,
            "trans_amount": 18000,
            "print_content": "유튜브 정기결제",
            "trans_type": "출금",
            "trans_method": "자동이체",
            "trans_date": datetime.now().date(),
            "trans_time": datetime.now().time(),
        }

    def test_transaction_create(self):
        transaction = Transaction.objects.create(**self.transaction_data)

        self.assertEqual(transaction.account_id, self.transaction_data["account_id"])
        self.assertEqual(transaction.trans_amount, self.transaction_data["trans_amount"])
        self.assertEqual(transaction.after_balance, self.account.balance - self.transaction_data["trans_amount"])
        self.assertEqual(transaction.print_content, self.transaction_data["print_content"])
        self.assertEqual(transaction.trans_type, self.transaction_data["trans_type"])
        self.assertEqual(transaction.trans_method, self.transaction_data["trans_method"])
        self.assertEqual(transaction.trans_date, self.transaction_data["trans_date"])
        self.assertEqual(transaction.trans_time, self.transaction_data["trans_time"])

    def test_transaction_update(self):
        transaction = Transaction.objects.create(**self.transaction_data)
        transaction.trans_amount = 20000

        transaction.save()

        transaction.refresh_from_db()
        self.assertEqual(transaction.trans_amount, 20000)
        self.assertEqual(transaction.after_balance, 980000)

    def test_transaction_delete(self):
        transaction = Transaction.objects.create(**self.transaction_data)

        transaction.delete()

        self.assertFalse(Transaction.objects.filter(id=transaction.id).exists())

    def test_transaction_delete_when_account_deleted(self):
        account = Account.objects.get(id=self.account.id)
        Transaction.objects.create(**self.transaction_data)

        account.delete()

        self.assertFalse(Account.objects.filter(id=self.account.id).exists())
        self.assertFalse(Transaction.objects.filter(account_id=self.account.id).exists())

    def test_transaction_delete_when_user_deleted(self):
        user = get_user_model().objects.get(id=self.user.id)
        Transaction.objects.create(**self.transaction_data)

        user.delete()

        self.assertFalse(get_user_model().objects.filter(id=self.user.id).exists())
        self.assertFalse(Account.objects.filter(user_id=self.user.id).exists())
        self.assertFalse(Transaction.objects.filter(account__user_id=self.user.id).exists())


class TransactionViewTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword1234",
            nickname="testuser",
            name="홍길동",
            phone="010-1111-2222",
        )
        self.account = Account.objects.create(
            user_id=self.user.id,
            account_num="3333-54-1231231",
            bank_code="090",
            balance=1000000,
            type="입출금"
        )
        self.access_token = str(RefreshToken.for_user(self.user).access_token)

    def test_transaction_create_view(self):
        url = reverse('transaction-create')
        data = {
            "account_id": self.account.id,
            "trans_amount": 18000,
            "print_content": "유튜브 구독 정기결제",
            "trans_type": "출금",
            "trans_method": "자동이체",
            "trans_date": datetime.now().date(),
            "trans_time": datetime.now().time(),
        }

        response = self.client.post(url, data, headers={"Authorization": f"Bearer {self.access_token}"})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(response.data["account"], data["account_id"])
        self.assertEqual(response.data["trans_amount"], data["trans_amount"])
        self.assertEqual(response.data["print_content"], data["print_content"])
        self.assertEqual(response.data["trans_type"], data["trans_type"])
        self.assertEqual(response.data["trans_method"], data["trans_method"])
        self.assertEqual(response.data["trans_date"], data["trans_date"].strftime("%Y-%m-%d"))
        self.assertEqual(response.data["trans_time"], data["trans_time"].strftime("%H:%M:%S"))

    def test_transaction_create_view_failed_by_negative_amount(self):
        url = reverse('transaction-create')
        data = {
            "account_id": self.account.id,
            "trans_amount": -18000,
            "print_content": "유튜브 구독 정기결제",
            "trans_type": "출금",
            "trans_method": "자동이체",
            "trans_date": datetime.now().date(),
            "trans_time": datetime.now().time(),
        }

        response = self.client.post(url, data, headers={"Authorization": f"Bearer {self.access_token}"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Transaction.objects.count(), 0)
        self.assertEqual(response.data["detail"], "거래금액은 원화 최소 단위인 10원보다 커야합니다.")

    def test_transaction_create_view_failed_by_amount_less_than_account_balance(self):
        url = reverse('transaction-create')
        data = {
            "account_id": self.account.id,
            "trans_amount": 1118000,
            "print_content": "유튜브 구독 정기결제",
            "trans_type": "출금",
            "trans_method": "자동이체",
            "trans_date": datetime.now().date(),
            "trans_time": datetime.now().time(),
        }

        response = self.client.post(url, data, headers={"Authorization": f"Bearer {self.access_token}"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Transaction.objects.count(), 0)
        self.assertEqual(response.data["detail"], "계좌 잔액보다 큰 금액은 출금할 수 없습니다.")

    def test_transaction_list_view(self):
        url = reverse('transaction-list')
        for i in range(30):
            Transaction.objects.create(
                account_id=self.account.id,
                trans_amount=random.randint(10000, 100000),
                print_content=f"{i + 1}. 입금 Test",
                trans_type="입금",
                trans_method="계좌이체",
                trans_date=datetime.now() + timedelta(days=i),
                trans_time=datetime.now().time(),
            )
            Transaction.objects.create(
                account_id=self.account.id,
                trans_amount=random.randint(10000, 100000),
                print_content=f"{i + 1}. 출금 Test",
                trans_type="출금",
                trans_method="자동이체",
                trans_date=datetime.now() + timedelta(days=i),
                trans_time=datetime.now().time(),
            )

        response = self.client.get(url, headers={"Authorization": f"Bearer {self.access_token}"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 30)
        self.assertEqual(response.data["deposit"][0]["print_content"], "30. 입금 Test")
        self.assertEqual(response.data["withdraw"][0]["print_content"], "30. 출금 Test")

    def test_transaction_detail_view(self):
        transaction = Transaction.objects.create(
            account_id=self.account.id,
            trans_amount=18000,
            print_content="유튜브 구독 정기결제",
            trans_type="출금",
            trans_method="자동이체",
            trans_date=datetime.now().date(),
            trans_time=datetime.now().time(),
        )
        url = reverse('transaction-detail', kwargs={'pk': transaction.id})

        response = self.client.get(url, headers={"Authorization": f"Bearer {self.access_token}"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], transaction.id)
        self.assertEqual(response.data["trans_amount"], transaction.trans_amount)
        self.assertEqual(response.data["print_content"], transaction.print_content)
        self.assertEqual(response.data["trans_type"], transaction.trans_type)
        self.assertEqual(response.data["trans_method"], transaction.trans_method)
        self.assertEqual(response.data["trans_date"], transaction.trans_date.strftime("%Y-%m-%d"))
        self.assertEqual(response.data["trans_time"], transaction.trans_time.strftime("%H:%M:%S"))
        self.assertEqual(response.data["after_balance"], transaction.after_balance)

    def test_transaction_update_view(self):
        transaction = Transaction.objects.create(
            account_id=self.account.id,
            trans_amount=18000,
            print_content="유튜브 구독 정기결제",
            trans_type="출금",
            trans_method="자동이체",
            trans_date=datetime.now().date(),
            trans_time=datetime.now().time(),
        )
        update_data = {
            "trans_amount": 20000,
        }
        url = reverse('transaction-detail', kwargs={'pk': transaction.id})


        response = self.client.put(url, update_data, headers={"Authorization": f"Bearer {self.access_token}"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["trans_amount"], update_data["trans_amount"])
        self.assertEqual(response.data["after_balance"], self.account.balance - update_data["trans_amount"])

    def test_transaction_delete_view(self):
        transaction = Transaction.objects.create(
            account_id=self.account.id,
            trans_amount=18000,
            print_content="유튜브 구독 정기결제",
            trans_type="출금",
            trans_method="자동이체",
            trans_date=datetime.now().date(),
            trans_time=datetime.now().time(),
        )
        url = reverse('transaction-delete', kwargs={'pk': transaction.id})

        response = self.client.put(url,headers={"Authorization": f"Bearer {self.access_token}"})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data["detail"], "거래내역이 성공적으로 삭제되었습니다.")
        self.assertFalse(Transaction.objects.filter(id=transaction.id).exists())
