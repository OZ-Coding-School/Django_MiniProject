from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from transactions.models import Transaction
from transactions.serializers import TransactionDetailSerializer, TransactionSerializer


class TransactionListCreateView(ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        date = self.request.query_params.get("date", "")
        if date:
            queryset = queryset.filter(trans_date=date)
        trans_type = self.request.query_params.get("trans_type", "")
        if trans_type:
            queryset = queryset.filter(trans_type=trans_type)
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return response
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TransactionDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionDetailSerializer

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        response.data = {"detail": "거래내역이 성공적으로 삭제되었습니다."}
        return response
