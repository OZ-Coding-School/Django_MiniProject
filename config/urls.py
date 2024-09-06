from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("accounts/", include("accounts.urls")),
    path("transactions/", include("transactions.urls")),
    path("analysis/", include("analysis.urls")),
    path("notifications/", include("notifications.urls")),
]
