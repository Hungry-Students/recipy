# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-20 11:42
from __future__ import unicode_literals

from django.db import migrations, models

from activitypub.models import uri


def ap_ids(apps, schema_editor):
    Person = apps.get_model("activitypub", "Person")
    Note = apps.get_model("activitypub", "Note")

    for person in Person.objects.all():
        ap_id = uri("person", person.username)
        person.ap_id = ap_id
        person.save()
    for note in Note.objects.all():
        ap_id = uri("note", note.person.username, note.id)
        note.ap_id = ap_id
        note.save()


class Migration(migrations.Migration):

    dependencies = [
        ("activitypub", "0004_auto_20170717_1749"),
    ]

    operations = [
        migrations.RenameField(
            model_name="person",
            old_name="actor_id",
            new_name="ap_id",
        ),
        migrations.AddField(
            model_name="note",
            name="ap_id",
            field=models.TextField(default="default"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="note",
            name="likes",
            field=models.ManyToManyField(related_name="liked", to="activitypub.Person"),
        ),
        migrations.AddField(
            model_name="note",
            name="remote",
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.RunPython(ap_ids, reverse_code=migrations.RunPython.noop),
    ]
