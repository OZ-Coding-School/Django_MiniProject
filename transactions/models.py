from django.db import models
from config.constants import TRANSACTION_TYPE, TRANSACTION_METHOD


class Transaction(models.Model):
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='transactions')
    trans_amount = models.IntegerField()
    after_balance = models.IntegerField()
    print_content = models.CharField(max_length=100)
    trans_type = models.CharField(choices=TRANSACTION_TYPE, max_length=20)
    trans_method = models.CharField(choices=TRANSACTION_METHOD, max_length=20)
    trans_date = models.DateField()
    trans_time = models.TimeField()

    def __str__(self):
        return f"{self.print_content} - {self.trans_amount}원"

    def validate_trans_amount(self):
        """
        거래 금액의 유효성을 검증하는 메서드입니다.
        """
        if self.trans_amount < 10:
            raise ValueError("거래금액은 원화 최소 단위인 10원보다 커야합니다.")

        if self.get_trans_type_display() == '출금' and self.trans_amount > self.account.balance:
            raise ValueError("계좌 잔액보다 큰 금액은 출금할 수 없습니다.")

    def set_after_balance(self):
        """
        거래 후 잔액을 설정하는 메서드입니다.
        이 메서드는 validate_trans_amount 메서드 후에 호출되어야 합니다.
        """
        self.validate_trans_amount()

        trans_type = self.get_trans_type_display()

        if trans_type == '입금':
            self.after_balance = self.account.balance + self.trans_amount
        elif trans_type == '출금':
            self.after_balance = self.account.balance - self.trans_amount

    def save(self, *args, **kwargs):
        """
        만약 객체를 저장하기 전에 after_balance가 지정되어있지 않다면 자동으로 계산하여 설정합니다.
        """
        # 거래 후 잔액을 설정하는 메서드 호출
        self.set_after_balance()

        # 부모 클래스의 save 메서드를 호출하여 데이터베이스에 저장
        return super().save(*args, **kwargs)
