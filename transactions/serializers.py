from rest_framework import serializers
from transactions.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['after_balance',]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["trans_type"] = instance.get_trans_type_display()
        data["trans_method"] = instance.get_trans_method_display()
        return data


class TransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        depth = 1

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["trans_type"] = instance.get_trans_type_display()
        data["trans_method"] = instance.get_trans_method_display()
        data['account']["account_num"] = instance.account.masking_account_num()
        return data
