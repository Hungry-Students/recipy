# Generated by Django 3.1.5 on 2021-02-09 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20210209_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cook_time',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
