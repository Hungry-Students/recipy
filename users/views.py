# -*- coding: utf-8 -*-
from django.shortcuts import render
from .models import User, RecipeDate, Recipe

def dashboard(request):
    return render(request, 'users/dashboard.html', context)

def cookbook(request, username):
    user = User.objects.filter(username=username)[0]
    user_recipes = user.recipes.all()
    context = {
        'recipes': user_recipes,
    }
    return render(request, 'TODO', context)
