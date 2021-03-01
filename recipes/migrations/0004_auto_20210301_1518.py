# Generated by Django 3.1.7 on 2021-03-01 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0003_auto_20210301_1040"),
    ]

    operations = [
        migrations.AddField(
            model_name="entry",
            name="ap_id",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="entry",
            name="remote",
            field=models.BooleanField(default=False),
        ),
    ]
