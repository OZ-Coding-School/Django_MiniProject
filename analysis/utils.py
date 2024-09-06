from datetime import datetime
from dateutil.relativedelta import relativedelta


class DateUtils:
    def __init__(self):
        self.today = datetime.today()

    def get_this_week_start(self):
        return self.today - relativedelta(days=self.today.weekday())

    def get_this_week_end(self):
        return self.get_this_week_start() + relativedelta(days=6)

    def get_last_week_start(self):
        return self.get_this_week_start() - relativedelta(weeks=1)

    def get_last_week_end(self):
        return self.get_last_week_start() + relativedelta(days=6)

    def get_next_month(self):
        return datetime(self.today.year, self.today.month, 1) + relativedelta(months=1)

    def get_this_month_end(self):
        return self.get_next_month() - relativedelta(days=1)

    def get_this_month_start(self):
        return datetime(self.today.year, self.today.month, 1)

    def get_last_month_start(self):
        return self.get_this_month_start() - relativedelta(months=1)

    def get_last_month_end(self):
        return self.get_this_month_start() - relativedelta(days=1)
