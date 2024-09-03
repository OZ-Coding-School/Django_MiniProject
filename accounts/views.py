from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from accounts.models import Account
from accounts.serializers import AccountDetailSerializer, AccountSerializer


class AccountListCreateView(ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AccountDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountDetailSerializer

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
