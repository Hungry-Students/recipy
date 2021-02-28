# -*- coding: utf-8 -*-
from django.urls import include, path

from users.views import dashboard, follow_toggle

app_name = "users"
urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("dashboard/", dashboard, name="dashboard"),
    path("follow/", follow_toggle, name="follow"),
]
