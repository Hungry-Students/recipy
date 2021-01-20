# -*- coding: utf-8 -*-
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from .models import Ingredient, RecipeCategory, RestrictedDiet, Recipe, IngredientQuantity
from django.urls import reverse


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
    	'error_message' : None,
    	'existing_recipe' : None,
    }
    return render(request , 'recipes/write.html', context)
    
def handle_form(request):

	#checking for duplicatas of recipies
	temp = Recipe.objects.filter(name = request.POST['title'])
	if temp:
		#re-render form with an error message. TODO : factor this (tutorial 4 at the end)
		ingredient_list = Ingredient.objects.order_by('name')
		context = {
			'range':range(1,6),
			'ingredient_list' : ingredient_list,
			'error_message' : 'this recipe already exists',
			'existing_recipe' : temp[0],
		}
		return render(request , 'recipes/write.html', context)
	
	#extracting ingredients and checking for ingredient duplicatas
	ingredient_quantities = {}
	ingredient_quantity_units = {}
	for i in range(1,6):
		ingredient_name = request.POST['ingredient'+str(i)]
		if ingredient_name == '':
			continue
		if ingredient_name in ingredient_quantities:
			#re-render form with an error message. TODO : factor this (tutorial 4 at the end)
			ingredient_list = Ingredient.objects.order_by('name')
			context = {
				'range':range(1,6),
				'ingredient_list' : ingredient_list,
				'error_message' : 'You have listed ingredient '+ingredient_name+' several times',
				'existing_recipe' : None,
			}
			return render(request , 'recipes/write.html', context)
		ingredient_quantities[ingredient_name] = request.POST['ingredient'+str(i)+'_quantity']
		ingredient_quantity_units[ingredient_name] = request.POST['ingredient'+str(i)+'_quantity_unit']
		
	#building new recipe
	new_recipe = Recipe(name = request.POST['title'], instruction = request.POST['instructions'], 
						quantity = request.POST['quantity'], quantity_unit = request.POST['quantity_unit'], 
						)
	new_recipe.save()
	#building Many-to-Many relatioships for ingredients
	
	for ingredient_name in ingredient_quantities.keys():
		ingredient_object = Ingredient.objects.filter(name = ingredient_name)[0]
		relation = IngredientQuantity(recipe = new_recipe, ingredient = ingredient_object,
									  quantity = ingredient_quantities[ingredient_name],
									  quantity_unit = ingredient_quantity_units[ingredient_name]
									 )
		relation.save()
	return HttpResponseRedirect(reverse('recipes:index'))
	
