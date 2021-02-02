# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from recipes.models import RecipeCategory
from .models import User, Cookbook, Entry

@login_required
def cookbook(request):
    user = request.user
    recipes = user.cookbook.recipes.all()
    categories = {'Miscellaneous': recipes.filter(category=None)}
    for category in RecipeCategory.objects.all():
        categories[category.name] = recipes.filter(category=category)
    context = { 'user': user,
                'recipes': recipes,
                'categories': categories,
               }
    return render(request, 'cookbook.html', context)

@login_required
def entry(request, entry_id):
    context = { 'user': request.user }
    cur_entry = Entry.objects.filter(id=entry_id)[0]
    context['entry'] = cur_entry
    return render(request, 'recipe.html', context)
