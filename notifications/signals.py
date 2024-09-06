from django.db.models.signals import post_save
from django.dispatch import receiver

from analysis.models import Analysis
from notifications.models import Notification


@receiver(post_save, sender=Analysis)
def send_analysis_confirm_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            message=f"{str(instance)}를 지금 확인해보세요!",
        )
        return

    Notification.objects.create(
        user=instance.user,
        message=f"수정된 {str(instance)}를 지금 확인해보세요!",
    )
