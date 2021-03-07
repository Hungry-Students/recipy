# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import Resolver404, resolve

import activities.activities as acts
from activities.views import outbox_follow

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
        if user_to_toggle.remote:
            follow_activity = acts.Follow(
                actor=user.to_activitystream(),
                object=user_to_toggle.to_activitystream(),
            )
            outbox_follow(follow_activity, user)
            # res = outbox_follow(follow_activity)
            # TODO: manage status code result

    url = request.GET.get("next")
    try:
        resolve(url)
        return HttpResponseRedirect(url)
    except Resolver404:
        return redirect("recipes:index")
