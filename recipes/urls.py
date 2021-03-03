# -*- coding: utf-8 -*-
from django.urls import path

from . import views

app_name = "recipes"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:recipe_id>/", views.recipe_detail, name="recipe_detail"),
    path("write", views.write, name="write"),
    path("handle_form", views.handle_form, name="handle_form"),
    path("update/<int:recipe_id>/", views.update, name="update"),
    path("scrape", views.scrape, name="scrape"),
    path("search", views.search, name="search"),
    path("cookbook/", views.my_cookbook, name="my_cookbook"),
    path("cookbook/<str:username>", views.cookbook, name="cookbook"),
    path("cookbook/<str:username>/<int:entry_id>/", views.entry, name="cookbook-entry"),
]
