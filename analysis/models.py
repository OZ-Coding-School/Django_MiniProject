from django.db import models

from config.constants import ANALYSIS_TYPES, ANALYSIS_ABOUT


class Analysis(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    about = models.CharField(choices=ANALYSIS_ABOUT, max_length=20)  # 수입에 대한 분석인지, 지출에 대한 분석인지
    type = models.CharField(choices=ANALYSIS_TYPES, max_length=7)  # 일간, 주간, 월간, 연간
    period_start = models.DateField()
    period_end = models.DateField()
    description = models.TextField()
    result_image = models.ImageField(upload_to='analysis/', null=True, blank=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.period_start.strftime('%Y-%m-%d')} ~ {self.period_end.strftime('%Y-%m-%d')} 기간의 {self.get_type_display()} {self.get_about_display()} 분석 결과"
