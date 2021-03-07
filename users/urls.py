# -*- coding: utf-8 -*-
from django.urls import include, path

from users.views import follow_toggle

app_name = "users"
urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("follow/", follow_toggle, name="follow"),
]
