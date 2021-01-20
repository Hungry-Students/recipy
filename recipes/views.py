# -*- coding: utf-8 -*-
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from .models import Ingredient, RecipeCategory, RestrictedDiet, Recipe, IngredientQuantity


def index(request):
	latest_recipes_list = Recipe.objects.order_by('-id')[:5]
	context = {
		'latest_recipes_list': latest_recipes_list,
	}
	return render(request, 'recipes/index.html', context)

def detail_recipe(request, recipe_id):
	recipe = Recipe.objects.filter(id=recipe_id)[0]
	ingredient_quantity_list = IngredientQuantity.objects.filter(recipe = recipe_id)
	context = {
		'recipe':recipe,
		'ingredient_quantities':ingredient_quantity_list,
	}
	return render(request, 'recipes/detail_recipe.html', context)

def write(request):
    # View that allows user to write their own recipes
    ingredient_list = Ingredient.objects.order_by('name')
    context = {
    	'range':range(1,6),
    	'ingredient_list' : ingredient_list,
    }
    return render(request , 'add/write.html', context)
