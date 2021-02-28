# -*- coding: utf-8 -*-
from django.urls import path

from . import views

app_name = "cookbook"
urlpatterns = [
    path("", views.my_cookbook, name="my_cookbook"),
    path("<str:username>", views.cookbook, name="cookbook"),
    path("<str:username>/<int:entry_id>/", views.entry, name="recipe"),
]
