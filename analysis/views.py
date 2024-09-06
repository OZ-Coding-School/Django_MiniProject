from rest_framework.generics import ListAPIView
from analysis.models import Analysis
from analysis.serializers import AnalysisSerializer


class AnalysisView(ListAPIView):
    queryset = Analysis.objects.all()
    serializer_class = AnalysisSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset.filter(user=self.request.user)
        return queryset
