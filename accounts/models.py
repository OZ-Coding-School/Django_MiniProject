from django.db import models
from config.constants import BANK_CODES, ACCOUNT_TYPE


class Account(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='accounts')
    account_num = models.CharField(max_length=50)
    bank_code = models.CharField(choices=BANK_CODES, max_length=3, default='000')
    type = models.CharField(choices=ACCOUNT_TYPE, max_length=20, default='CHECKING')
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.get_bank_code_display()}: {self.account_num[-4:]}"

    def masking_account_num(self):
        num_list = self.account_num.split('-')
        num_list[-1] = '*' * len(num_list[-1])
        return "-".join(num_list)
