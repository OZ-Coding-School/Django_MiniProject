from django.urls import path
from accounts import views as account_views


urlpatterns = [
    path("", account_views.AccountListCreateView.as_view(), name="account-list"),
    path("<int:pk>/", account_views.AccountDetailView.as_view(), name="account-detail"),
]