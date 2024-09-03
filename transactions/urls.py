from django.urls import path

from transactions import views as trans_views

urlpatterns = [
    path("", trans_views.TransactionListCreateView.as_view(), name="transaction-list"),
    path("<int:pk>/", trans_views.TransactionDetailView.as_view(), name="transaction-detail"),
]
