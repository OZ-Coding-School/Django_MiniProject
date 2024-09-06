from rest_framework.generics import ListAPIView, UpdateAPIView
from notifications.models import Notification
from notifications.serializers import NotificationSerializer


class NotificationListAPIView(ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user, is_read=False).order_by("-created_at")


class NotificationReadAPIView(UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_object(self):
        return Notification.objects.get(id=self.kwargs["pk"], user=self.request.user)
