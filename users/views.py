# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import Resolver404, resolve

from .models import User
from .utils import is_following


@login_required
def follow_toggle(request):
    user_to_toggle = get_object_or_404(
        User, username=request.POST.get("user_to_toggle")
    )
    user = request.user
    if is_following(user, user_to_toggle):
        user_to_toggle.followers.remove(user)
    else:
        user_to_toggle.followers.add(user)
    url = request.GET.get("next")
    try:
        resolve(url)
        return HttpResponseRedirect(url)
    except Resolver404:
        return redirect("recipes:index")
