# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from recipes.models import RecipeCategory
from users.utils import is_following

from .models import Entry, User


def cookbook(request, username):
    user = get_object_or_404(User, username=username)
    recipes = user.cookbook.recipes.all()
    categories = {"Miscellaneous": recipes.filter(category=None)}
    for category in RecipeCategory.objects.all():
        categories[category.name] = recipes.filter(category=category)
    is_following_ = is_following(request.user, user)
    context = {
        "user": user,
        "recipes": recipes,
        "categories": categories,
        "is_following": is_following_,
    }
    return render(request, "cookbook/cookbook.html", context)


@login_required
def my_cookbook(request):
    username = request.user.username
    return redirect("cookbook:cookbook", username=username)


def entry(request, entry_id, username):
    user = get_object_or_404(User, username=username)
    cur_entry = get_object_or_404(Entry, id=entry_id)
    context = {
        "user": user,
        "entry": cur_entry,
    }
    return render(request, "cookbook/recipe.html", context)
