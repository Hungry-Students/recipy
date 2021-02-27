# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import Resolver404, resolve
from django.contrib.auth.decorators import login_required
from .models import User
from .utils import is_following

def dashboard(request):
    return render(request, 'users/dashboard.html')

@login_required
def follow_toggle(request, *args, **kwargs):
    user_to_toggle = get_object_or_404(User, username=request.POST.get('user_to_toggle'))
    user = request.user
    if is_following(user, user_to_toggle):
        user_to_toggle.followers.remove(user)
    else:
        user_to_toggle.followers.add(user)
    url = request.GET.get('next')
    try:
        resolve(url)
        return HttpResponseRedirect(url)
    except Resolver404:
        return redirect('users:dashboard')
