# -*- coding: utf-8 -*-
from django.urls import path, include
from users.views import dashboard, follow_toggle

app_name='users'
urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('dashboard/', dashboard, name='dashboard'),
    path('follow/', follow_toggle, name='follow')
]
