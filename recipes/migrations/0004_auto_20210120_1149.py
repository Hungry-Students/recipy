# Generated by Django 3.1.5 on 2021-01-20 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20210120_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cook_time',
            field=models.DurationField(blank=True, null=True),
        ),
    ]
