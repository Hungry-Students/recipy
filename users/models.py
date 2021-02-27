# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers')

    def __str__(self):
        return self.username
