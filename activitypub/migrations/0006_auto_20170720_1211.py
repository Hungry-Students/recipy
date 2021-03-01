# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-20 12:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("activitypub", "0005_auto_20170720_1142"),
    ]

    operations = [
        migrations.AlterField(
            model_name="note",
            name="ap_id",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="note",
            name="remote",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="person",
            name="ap_id",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="person",
            name="remote",
            field=models.BooleanField(default=False),
        ),
    ]