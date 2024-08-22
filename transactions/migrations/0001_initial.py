# Generated by Django 5.1 on 2024-08-22 07:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0002_rename_account_type_account_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("trans_amount", models.IntegerField()),
                ("after_balance", models.IntegerField()),
                ("print_content", models.CharField(max_length=100)),
                ("trans_type", models.CharField(max_length=20)),
                ("trans_method", models.CharField(max_length=20)),
                ("trans_date", models.DateTimeField(auto_now_add=True)),
                ("trans_time", models.TimeField(auto_now_add=True)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to="accounts.account"
                    ),
                ),
            ],
        ),
    ]
