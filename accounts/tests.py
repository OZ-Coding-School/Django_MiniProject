from django.test import TestCase
from django.contrib.auth import get_user_model
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
            'user_id': self.user.id,
            'account_num': '3333-54-1231231',
            'bank_code': '090',
            'balance': 1000000,
            'type': '입출금통장'
        }

    def test_create_account(self):
        account = Account.objects.create(**self.account_data)

        self.assertEqual(account.user_id, self.user.id)
        self.assertEqual(account.account_num, self.account_data['account_num'])
        self.assertEqual(account.bank_code, self.account_data['bank_code'])
        self.assertEqual(account.balance, self.account_data['balance'])
        self.assertEqual(account.type, self.account_data['type'])

    def test_update_account_balance(self):
        account = Account.objects.create(**self.account_data)
        self.assertEqual(account.balance, self.account_data['balance'])
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
