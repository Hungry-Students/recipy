# Generated by Django 3.1.7 on 2021-03-02 13:18

import annoying.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recipes", "0004_auto_20210301_1518"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cookbook",
            name="owner",
            field=annoying.fields.AutoOneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                related_name="cookbook",
                serialize=False,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]