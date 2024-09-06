from django.urls import path

from . import views as analysis_views

urlpatterns = [
    path("", analysis_views.AnalysisView.as_view(), name="analysis"),
]
