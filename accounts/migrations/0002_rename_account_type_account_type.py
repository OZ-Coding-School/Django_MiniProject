# Generated by Django 5.1 on 2024-08-22 06:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="account",
            old_name="account_type",
            new_name="type",
        ),
    ]
