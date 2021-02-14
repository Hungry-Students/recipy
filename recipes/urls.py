# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'recipes'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('write', views.write, name='write'),
    path('handle_form', views.handle_form, name='handle_form'),
    path('scrape', views.scrape, name='scrape'),
    path('search', views.search, name='search'),
]
