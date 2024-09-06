from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.is_read = True
        instance.save()
        return instance
