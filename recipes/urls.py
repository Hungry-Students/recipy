# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'recipes'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:recipe_id>/', views.detail_recipe, name='detail_recipe'),
    path('write', views.write, name='write'),
    path('handle_form', views.handle_form, name='handle_form'),
    path('scrape', views.scrape, name='scrape'),
]
