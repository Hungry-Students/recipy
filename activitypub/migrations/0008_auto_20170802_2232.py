# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-02 22:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activitypub', '0007_activity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='remote',
            field=models.BooleanField(default=False),
        ),
    ]
