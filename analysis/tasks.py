from celery import shared_task
from django.contrib.auth import get_user_model

from analysis.analyzers import SpendingAnalyzer

User = get_user_model()
Analyzer = SpendingAnalyzer


@shared_task
def weekly_analyze_and_notify_user():
    users = User.objects.all()

    for user in users:
        analyzer = Analyzer(user.id)
        analyzer.make_matplot_weekly_spending()


@shared_task
def monthly_analyze_and_notify_user():
    users = User.objects.all()

    for user in users:
        analyzer = Analyzer(user.id)
        analyzer.make_matplot_monthly_spending()
