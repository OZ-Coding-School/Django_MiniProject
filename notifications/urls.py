from django.urls import path
from notifications import views as notification_views

urlpatterns = [
    path('', notification_views.NotificationListAPIView.as_view(), name="notification-list"),
    path('<int:pk>/read/', notification_views.NotificationReadAPIView.as_view(), name="notification-read"),
]