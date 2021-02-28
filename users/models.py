# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers"
    )

    def __str__(self):
        return str(self.username)
