# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name='cookbook'
urlpatterns = [
    path('', views.cookbook, name='cookbook'),
    path('recipe/<int:entry_id>/', views.entry, name='recipe'),
]
