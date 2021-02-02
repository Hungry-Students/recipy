# -*- coding: utf-8 -*-
from django.shortcuts import render
from .models import User

def dashboard(request):
    return render(request, 'users/dashboard.html')
