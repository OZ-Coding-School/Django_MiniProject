from datetime import datetime

from django.test import TestCase

from django.contrib.auth import get_user_model


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
            user_id=self.user.id,
            account_num='3333-54-1231231',
            bank_code='090',
            balance=1000000,
            type='입출금통장'
        )
        self.transaction_data = {
            'account_id': self.account.id,
            'trans_amount': 18000,
            'after_balance': 982000,
            'print_content': '자동이체',
            'trans_type': '출금',
            'trans_method': '유튜브 정기결제',
            'trans_date': datetime.now(),
            'trans_time': datetime.now().time()
        }

    def test_transaction_create(self):
        transaction = Transaction.objects.create(**self.transaction_data)

        self.assertEqual(transaction.account_id, self.transaction_data['account_id'])
        self.assertEqual(transaction.trans_amount, self.transaction_data['trans_amount'])
        self.assertEqual(transaction.after_balance, self.transaction_data['after_balance'])
        self.assertEqual(transaction.print_content, self.transaction_data['print_content'])
        self.assertEqual(transaction.trans_type, self.transaction_data['trans_type'])
        self.assertEqual(transaction.trans_method, self.transaction_data['trans_method'])
        self.assertEqual(transaction.trans_date, self.transaction_data['trans_date'])
        self.assertEqual(transaction.trans_time, self.transaction_data['trans_time'])

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