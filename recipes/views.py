# -*- coding: utf-8 -*-
import re
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect #, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from recipe_scrapers import scrape_me, WebsiteNotImplementedError
from .models import Ingredient, Recipe, IngredientQuantity, RecipeCategory, RestrictedDiet, Comment
from .parser import IngredientParser, YieldsParser
from .forms import InputRecipeForm, CommentForm

def index(request):
    latest_recipes_list = Recipe.objects.order_by('-id')[:5]
    context = {
        'latest_recipes_list': latest_recipes_list,
    }
    return render(request, 'recipes/index.html', context)

def recipe_detail(request, recipe_id):
    recipe = Recipe.objects.filter(id=recipe_id)[0]
    comments = recipe.comments.all
    new_comment = None
    # Check whether a comment is being posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.recipe = recipe
            new_comment.user = request.user
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()
    context = {
        'recipe': recipe,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
    }
    return render(request, 'recipes/recipe_detail.html', context)

### SUBMITTING RECIPES ###

@login_required
def write(request, error_message_link=None, error_message_form=None, existing_recipe=None):
    form = InputRecipeForm(initial = {'quantity_unit' : 'servings'})
    context = {
        'error_message_link' : error_message_link,
        'error_message_form' : error_message_form,
        'existing_recipe' : existing_recipe,
        'form' : form,
    }
    return render(request , 'recipes/write.html', context)

### SUBMITTING VIA A FORM ###

def handle_form(request):
    form = InputRecipeForm(request.POST)
    if form.is_valid():
    	form.save()
    	return HttpResponseRedirect(reverse('recipes:index'))
    print(form.errors)
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
