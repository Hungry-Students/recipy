# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


def uri(name, *args):
    """
    Reverse name 'name' (using arguments 'args') and return the corresponding URI
    """
    domain = settings.ACTIVITYPUB_DOMAIN
    path = reverse(name, args=args)
    return "http://{domain}{path}".format(domain=domain, path=path)


class URIs:
    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)


class User(AbstractUser):
    # Corresponds to the Person actor type of Activity Streams
    # https://www.w3.org/ns/activitystreams#Person
    ap_id = models.TextField(null=True)
    remote = models.BooleanField(default=False)

    following = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers"
    )

    @property
    def uris(self):
        if self.remote:
            return URIs(id=self.ap_id)
        return URIs(
            id=uri("activities:person", self.username),
            following=uri("activities:following", self.username),
            followers=uri("activities:followers", self.username),
            outbox=uri("activities:outbox", self.username),
            inbox=uri("activities:inbox", self.username),
        )

    def to_activitystream(self):
        activitystream_json = {
            "type": "Person",
            "id": self.uris.id,
            "name": self.username,  # TODO: update this with real name
            "preferredUsername": self.username,
        }

        if not self.remote:
            activitystream_json.update(
                {
                    "following": self.uris.following,
                    "followers": self.uris.followers,
                    "outbox": self.uris.outbox,
                    "inbox": self.uris.inbox,
                }
            )
        return activitystream_json

    def __str__(self):
        return str(self.username)
