# -*- coding: utf-8 -*-
# Generated by Django 3.1.5 on 2021-02-02 15:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20210126_1611'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='recipes',
        ),
        migrations.DeleteModel(
            name='RecipeDate',
        ),
    ]
