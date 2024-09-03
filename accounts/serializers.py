from rest_framework import serializers
from accounts.models import Account
from transactions.serializers import TransactionSerializer


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"
        read_only_fields = ("id", "user")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["bank_name"] = instance.get_bank_code_display()
        data["type"] = instance.get_type_display()
        data["account_num"] = instance.masking_account_num()
        return data


class AccountDetailSerializer(AccountSerializer):
    transactions = serializers.SerializerMethodField()

    def get_transactions(self, obj):
        transactions = obj.transactions.all()

        if not transactions.exists():
            return []

        return TransactionSerializer(transactions, many=True).data
