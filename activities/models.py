import json

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from recipes.models import Entry
from users.models import URIs, User, uri


class Activity(models.Model):
    ap_id = models.TextField()
    payload = models.BinaryField()
    created_at = models.DateField(auto_now_add=True)
    person = models.ForeignKey(
        User, related_name="activities", on_delete=models.CASCADE
    )
    remote = models.BooleanField(default=False)

    @property
    def uris(self):
        if self.remote:
            ap_id = self.ap_id
        else:
            ap_id = uri("activity", self.person.username, self.id)
        return URIs(id=ap_id)

    def to_activitystream(self):
        payload = self.payload.decode("utf-8")
        data = json.loads(payload)
        data.update({"id": self.uris.id})
        return data


@receiver(post_save, sender=User)
@receiver(post_save, sender=Entry)
@receiver(post_save, sender=Activity)
def save_ap_id(sender, instance, created, **kwargs):
    if created and not instance.remote:
        instance.ap_id = instance.uris.id
        instance.save()
