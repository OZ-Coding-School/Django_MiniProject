import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
from django.conf import settings
from django.contrib.auth import get_user_model

from analysis.models import Analysis
from analysis.utils import DateUtils
from transactions.models import Transaction

User = get_user_model()

plt.rcParams['font.family'] = "AppleGothic"


class SpendingAnalyzer(DateUtils):
    def __init__(self, user_id):
        super().__init__()
        self.user = User.objects.get(id=user_id)
        self.queryset = Transaction.objects.filter(account__user=self.user, trans_type="WITHDRAW")

    def get_this_week_transactions(self):
        return self.queryset.filter(
            trans_date__range=[self.get_this_week_start(), self.get_this_week_end()]
        )

    def get_last_week_transactions(self):
        return self.queryset.filter(
            trans_date__range=[self.get_last_week_start(), self.get_last_week_end()]
        )

    def get_this_month_transactions(self):
        return self.queryset.filter(
            trans_date__range=[self.get_this_month_start(), self.get_this_month_end()]
        )

    def get_last_month_transactions(self):
        return self.queryset.filter(
            trans_date__range=[self.get_last_month_start(), self.get_last_month_end()]
        )

    def analyze_total_spending(self, transactions):
        # DataFrame으로 변환하여 분석
        transactions_df = pd.DataFrame(list(transactions.values('trans_date', 'trans_amount', 'trans_type')))
        # 소비 분석
        spending_analysis = transactions_df.groupby('trans_type')['trans_amount'].sum()

        return spending_analysis

    def make_matplot_weekly_spending(self):
        this_week_transactions = self.get_this_week_transactions()
        last_week_transactions = self.get_last_week_transactions()
        if this_week_transactions.count() == 0 or last_week_transactions.count() == 0:
            raise ValueError("No enough transactions data available.")
        this_weekly_spending_analysis = self.analyze_total_spending(this_week_transactions)
        last_weekly_spending_analysis = self.analyze_total_spending(last_week_transactions)

        categories = this_weekly_spending_analysis.index
        this_week_values = this_weekly_spending_analysis.values
        last_week_values = last_weekly_spending_analysis.reindex(categories, fill_value=0).values

        fig, ax = plt.subplots()

        # 막대 위치 설정
        x = np.arange(len(categories))  # x 좌표
        width = 0.4  # 막대 너비

        # 막대 그래프 그리기
        ax.bar(x - width / 2, this_week_values, width, color='green', alpha=0.7, label='이번 주')
        ax.bar(x + width / 2, last_week_values, width, color='red', alpha=0.7, label='지난 주')

        # 그래프 레이블 및 제목 설정
        ax.set_ylabel('지출 금액')
        ax.set_xlabel('주간별')
        ax.set_title('지난 주 - 이번 주 주간 총 지출금액 비교')
        ax.set_xticks(x)
        ax.legend()

        # 그래프의 레이아웃 자동 조정
        plt.tight_layout()

        plot_image = self.save_plot_image(plt, "weekly")

        Analysis.objects.create(
            user=self.user,
            period_start=self.get_last_week_start(),
            period_end=self.get_this_week_end(),
            about="TOTAL_SPENDING",
            type='WEEKLY',
            result_image=plot_image
        )

    def make_matplot_monthly_spending(self):
        this_monthly_spending_analysis = self.analyze_total_spending(self.get_this_month_transactions())
        if this_monthly_spending_analysis.empty:
            raise ValueError("No this_monthly_spending_analysis data available.")

        last_monthly_spending_analysis = self.analyze_total_spending(self.get_last_month_transactions())
        if last_monthly_spending_analysis.empty:
            raise ValueError("No last_monthly_spending_analysis data available.")

        categories = this_monthly_spending_analysis.index
        this_month_values = this_monthly_spending_analysis.values
        last_month_values = last_monthly_spending_analysis.reindex(categories, fill_value=0).values

        fig, ax = plt.subplots()

        # 막대 위치 설정
        x = np.arange(len(categories))  # x 좌표
        width = 0.4  # 막대 너비

        # 막대 그래프 그리기
        ax.bar(x - width / 2, this_month_values, width, color='green', alpha=0.7, label='이번 달')
        ax.bar(x + width / 2, last_month_values, width, color='red', alpha=0.7, label='지난 달')

        # 그래프 레이블 및 제목 설정
        ax.set_ylabel('지출 금액')
        ax.set_xlabel('월별')
        ax.set_title('저번 달 - 이번 달 월간 총 지출금액 비교')
        ax.set_xticks(x)
        ax.legend()

        # 그래프의 레이아웃 자동 조정
        plt.tight_layout()

        plot_image = self.save_plot_image(plt, "monthly")

        Analysis.objects.create(
            user=self.user,
            about="TOTAL_SPENDING",
            period_start=self.get_last_month_start(),
            period_end=self.get_this_month_end(),
            type='MONTHLY',
            result_image=plot_image
        )

    def save_plot_image(self, plot, prefix):
        # 이미지 파일을 static 경로에 저장
        today = self.today.strftime("%Y-%m-%d")
        static_dir = os.path.join(
            settings.BASE_DIR, 'media', f'analysis/total_spending/{today}'
        )
        os.makedirs(static_dir, exist_ok=True)

        filename = f'{prefix}_total_spending_{self.user.id}.png'
        filepath = os.path.join(static_dir, filename)
        plot.savefig(filepath)

        return filepath
