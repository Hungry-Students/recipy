# -*- coding: utf-8 -*-
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponseRedirect #, HttpResponse
from django.urls import reverse
from recipe_scrapers import scrape_me, WebsiteNotImplementedError
from .models import Ingredient, Recipe, IngredientQuantity #, RecipeCategory, RestrictedDiet
from .parser import IngredientParser, YieldsParser


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

### SUBMITTING RECIPES ###

def write(request, error_message_link=None, error_message_form=None, existing_recipe=None):
    '''View that allow users to submit their own recipes'''
    ingredient_list = Ingredient.objects.order_by('name')
    context = {
        'range':range(1,6),
        'ingredient_list' : ingredient_list,
        'error_message_link' : error_message_link,
        'error_message_form' : error_message_form,
        'existing_recipe' : existing_recipe,
    }
    return render(request , 'recipes/write.html', context)

### SUBMITTING VIA A FORM ###

def handle_form(request):

    #checking for duplicates of recipes
    temp = Recipe.objects.filter(name = request.POST['title'])
    if temp:
        return write(request, error_message_form = 'this recipe already exists', existing_recipe = temp[0])

    #extracting ingredients and checking for ingredient duplicates
    ingredient_quantities = {}
    ingredient_quantity_units = {}
    for i in range(1,6):
        ingredient_name = request.POST['ingredient'+str(i)]
        if ingredient_name == '':
            continue
        ingredient_name = ingredient_name.lower() #note : we enforce lower case here for ingredient name
        if ingredient_name in ingredient_quantities:
            return write(request, error_message_form = 'You have listed ingredient '+ingredient_name+' several times')
        ingredient_quantities[ingredient_name] = request.POST['ingredient'+str(i)+'_quantity']
        ingredient_quantity_units[ingredient_name] = request.POST['ingredient'+str(i)+'_quantity_unit'].lower() 
        #note : we enforce lower case here for ingredient quantity unit. If upper case is needed in representation (e.g. cL), it will be transformed later on

    #building new recipe
    new_recipe = Recipe(name = request.POST['title'],
                        instruction = request.POST['instructions'],
                        quantity = request.POST['quantity'],
                        quantity_unit = request.POST['quantity_unit'],
                        )
    new_recipe.save()

    #building Many-to-Many relationships for ingredients
    for ingredient_name in ingredient_quantities.keys():
        add_ingredient(new_recipe, ingredient_name, ingredient_quantities[ingredient_name], ingredient_quantity_units[ingredient_name])

    return HttpResponseRedirect(reverse('recipes:index'))


### SUBMITTING VIA RECIPE-SCRAPPER ###

def scrape(request):
	try:
		existing_recipes = Recipe.objects.filter(url = request.POST['url'])
		if not existing_recipes:
			scraper = scrape_me(request.POST['url'])
			yields_parser = YieldsParser()
			yields_parser.parse(scraper.yields())
			print(scraper.total_time())
			new_recipe = Recipe(name = scraper.title(),
								instruction = scraper.instructions(),
								quantity = yields_parser.yields,
								quantity_unit = yields_parser.yields_unit.lower(),
								url = request.POST['url']
								)
			new_recipe.save()
			ingredient_parser = IngredientParser()
			for e in scraper.ingredients():
				ingredient_parser.parse(e.lower()) #note : we enforce lower case in the argument, and will give upper case (e.g. cL) in the parser when needed
				add_ingredient(new_recipe, ingredient_parser.ingredient_name, ingredient_parser.quantity, ingredient_parser.quantity_unit)
		else:
			return write(request, error_message_link = 'this recipe already exists', existing_recipe = existing_recipes[0])
		return HttpResponseRedirect(reverse('recipes:index'))
	except WebsiteNotImplementedError:
		msg = 'the url '+ request.POST['url'] + ' is not supported by recipe_scraper'
		return write(request, error_message_link=msg)

### NON-VIEWS FUNCTION ###

def add_ingredient(recipe, ingredient_name, ingredient_quantity, ingredient_quantity_unit):
    #Fetching or creating ingredient
    possible_ing_obj = Ingredient.objects.filter(name = ingredient_name)
    if possible_ing_obj :
        ingredient_object = possible_ing_obj[0]
    else :
        ingredient_object = Ingredient(name = ingredient_name)
        ingredient_object.save()
        
    #Building relation to recipe
    relation = IngredientQuantity(recipe = recipe,
                                  ingredient = ingredient_object,
                                  quantity = ingredient_quantity,
                                  quantity_unit = ingredient_quantity_unit
                                  )
    relation.save()
