# Generated by Django 3.1.7 on 2021-03-07 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0006_merge_20210306_1756"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="ap_id",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="recipe",
            name="remote",
            field=models.BooleanField(default=False),
        ),
    ]
