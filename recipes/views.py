# -*- coding: utf-8 -*-
import re
from django.shortcuts import render
from django.http import HttpResponseRedirect #, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from recipe_scrapers import scrape_me, WebsiteNotImplementedError
from .models import Ingredient, Recipe, IngredientQuantity, RecipeCategory, RestrictedDiet
from .parser import IngredientParser, YieldsParser
from .forms import RecipeForm

def index(request):
    latest_recipes_list = Recipe.objects.order_by('-id')[:5]
    context = {
        'latest_recipes_list': latest_recipes_list,
    }
    return render(request, 'recipes/index.html', context)

def detail_recipe(request, recipe_id):
    recipe = Recipe.objects.filter(id=recipe_id)[0]
    context = {
        'recipe':recipe,
    }
    return render(request, 'recipes/detail_recipe.html', context)

### SUBMITTING RECIPES ###

@login_required
def write(request, error_message_link=None, error_message_form=None, existing_recipe=None):
    form = RecipeForm(initial = {'quantity_unit' : 'servings'})
    ingredient_list = Ingredient.objects.order_by('name')
    context = {
        'error_message_link' : error_message_link,
        'error_message_form' : error_message_form,
        'existing_recipe' : existing_recipe,
        'form' : form,
        'ingredient_list' : ingredient_list,
    }
    return render(request , 'recipes/write.html', context)

### SUBMITTING VIA A FORM ###

def handle_form(request):
    form = RecipeForm(request.POST)
    if form.is_valid():

        #checking for duplicates of recipes, we don't really want that anymore (was more of a proof of concept)
        """
        temp = Recipe.objects.filter(name = form.cleaned_data['name'])
        if temp:
            return write(request, error_message_form = 'this recipe already exists', existing_recipe = temp[0])"""

        #extracting ingredients and checking for ingredient duplicates. Note : we do that before saving the recipe to avoid incomplete recipes.
        ingredient_names = {}
        for e in request.POST.keys():
            m = re.search('ingredient(?P<id>[0-9]+)_name', e)
            if m is not None:
                ingredient_id = m.group('id')
                ingredient_name = request.POST[e]
                if ingredient_name == '':
                    continue
                ingredient_name = ingredient_name.lower() #note : we enforce lower case here for ingredient name
                if ingredient_name in ingredient_names.values():
                    return write(request, error_message_form = 'You have listed ingredient '+ingredient_name+' several times')
                ingredient_names[ingredient_id] = ingredient_name

        r = form.save()

        #Manage cook time
        cook_time_hours = request.POST.get('cook_time_hours', 0)
        if not cook_time_hours:
            cook_time_hours = 0
        cook_time_minutes = request.POST.get('cook_time_minutes', 0)
        if not cook_time_minutes:
            cook_time_minutes = 0

        r.cook_time = 60*int(cook_time_hours)+int(cook_time_minutes)
        r.save()

        #Parsing quantities and saving ingredients
        p = IngredientParser()
        for ingredient_id, ingredient_name in ingredient_names.items():
            ingredient_quantity, ingredient_unit = p.parse_quantity(request.POST.get('ingredient'+ingredient_id+'_quantity', ''))
            add_ingredient(r, ingredient_name, ingredient_quantity, ingredient_unit)

        return HttpResponseRedirect(reverse('recipes:index'))
    return write(request, error_message_form = 'Submitted an invalid form')

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
                ingredient_parser.parse(e.lower())
                # NOTE: we force lower case in the argument, upper case will be
                # given in the parser when needed (e.g. cL)
                add_ingredient(new_recipe, ingredient_parser.ingredient_name, ingredient_parser.quantity, ingredient_parser.quantity_unit)
        else:
            return write(request, error_message_link = 'this recipe already exists', existing_recipe = existing_recipes[0])
        return HttpResponseRedirect(reverse('recipes:index'))
    except WebsiteNotImplementedError:
        msg = 'the url '+ request.POST['url'] + ' is not supported by recipe_scraper'
        return write(request, error_message_link=msg)
        
        
### SEARCHING RECIPES ###
def search(request):
	ingredient_list = Ingredient.objects.order_by('name')
	recipe_category_list = RecipeCategory.objects.all()
	diet_list = RestrictedDiet.objects.all()
	if request.method == 'GET':
		context = {
			'ingredient_list' : ingredient_list,
			'recipe_category_list' : recipe_category_list,
			'diet_list' : diet_list,
			'results' : None,
			'has_results': False,
		}
		return render(request , 'recipes/search.html', context)
	else:
		#filtering name
		querry = Recipe.objects.filter(name__icontains = request.POST['recipe_name'])
		#filtering category
		if request.POST['recipe_category']:
			querry = querry.filter(category__name = request.POST['recipe_category'])
		#filtering diet
		for diet in request.POST.getlist('diets'):
			querry = querry.filter(diets__name=diet)
		#filtering ingredients
		for e in request.POST.keys():
			m = re.search('ingredient(?P<id>[0-9]+)_name', e)
			if m is not None:
				ingredient_id = m.group('id')
				ingredient_name = request.POST[e]
				if ingredient_name == '':
					continue
				ingredient_name = ingredient_name.lower() #note : ingredients are stored using lowercase
				if request.POST.get('exclude_'+ingredient_id,None):
					querry = querry.exclude(ingredients__name=ingredient_name)
				else:
					querry = querry.filter(ingredients__name=ingredient_name)
					                
		context = {
			'ingredient_list' : ingredient_list,
			'recipe_category_list' : recipe_category_list,
			'diet_list' : diet_list,
			'results' : querry,
			'has_results': True,
		}
		return render(request , 'recipes/search.html', context)

### Non view functions ###

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
