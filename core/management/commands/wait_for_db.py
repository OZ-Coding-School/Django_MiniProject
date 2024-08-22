import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as Psycopg2OpError


class Command(BaseCommand):
    help = 'Django command to wait for the database to be available'

    def handle(self, *args, **options):
        for i in range(10):
            self.stdout.write(f'Try {i}: Waiting for database...')
            try:
                connection = connections['default']
                if connection:
                    self.stdout.write(self.style.SUCCESS('PostgreSQL Database available!'))
                    return
            except (Psycopg2OpError, OperationalError):
                if i == 9:
                    self.stdout.write(self.style.FAIL(f"PostgreSQL Connection Failed after {i+1} attempts"))
                self.stdout.write(self.style.FAIL("PostgreSQL Connection Failed! Connection Retrying..."))
                time.sleep(1)