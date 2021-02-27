# -*- coding: utf-8 -*-
from .models import User

def is_following(potential_follower, potential_followed):
    return potential_follower in potential_followed.followers.all()
