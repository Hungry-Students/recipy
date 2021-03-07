# -*- coding: utf-8 -*-
# import re

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect  # , HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from recipe_scrapers import WebsiteNotImplementedError, scrape_me

from users.models import User
from users.utils import is_following

from .forms import CommentForm, InputRecipeForm, SearchRecipeForm, get_ingredient_list, form_from_scrape
from .models import (
    Cookbook,
    Entry,
    Ingredient,
    IngredientQuantity,
    Recipe,
    RecipeCategory,
)
from .parser import IngredientParser, YieldsParser


def index(request):
    cookbook_count = Cookbook.objects.count()
    latest_recipes_list = Recipe.objects.order_by("-id")[:5]
    context = {
        "latest_recipes_list": latest_recipes_list,
    }
    return render(request, "recipes/index.html", context)


def recipe_detail(request, recipe_id):
    recipe = Recipe.objects.filter(id=recipe_id)[0]
    comments = recipe.comments.all
    new_comment = None
    # Check whether a comment is being posted
    if request.method == "POST":
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
        "recipe": recipe,
        "comments": comments,
        "new_comment": new_comment,
        "comment_form": comment_form,
    }
    return render(request, "recipes/recipe_detail.html", context)


# COOKBOOKS


def cookbook(request, username):
    """
    Shows the cookbook of user "username"
    """
    user = get_object_or_404(User, username=username)
    recipes = user.cookbook.recipes.all()
    categories = {"My recipes": recipes.filter(category=None)}
    for category in RecipeCategory.objects.all():
        categories[category.name] = recipes.filter(category=category)
    is_following_ = is_following(request.user, user)
    context = {
        "user": user,
        "recipes": recipes,
        "categories": categories,
        "is_following": is_following_,
    }
    return render(request, "recipes/cookbook/cookbook.html", context)


@login_required
def my_cookbook(request):
    """
    Show the cookbook of request.user
    """
    username = request.user.username
    return redirect("recipes:cookbook", username=username)


def entry(request, recipe_id, username):
    """
    Show the entry (=recipe) "recipe_id" in user "username"'s cookbook
    """
    user = get_object_or_404(User, username=username)
    cur_entry = get_object_or_404(Entry, recipe__id=recipe_id, cookbook__owner=user)
    context = {
        "user": user,
        "entry": cur_entry,
    }
    return render(request, "recipes/cookbook/recipe.html", context)


# SUBMITTING RECIPES


@login_required
def write(
    request, error_message_link=None, error_message_form=None, existing_recipe=None
):
    form = InputRecipeForm(initial={"quantity_unit": "servings"})
    context = {
        "error_message_link": error_message_link,
        "error_message_form": error_message_form,
        "existing_recipe": existing_recipe,
        "form": form,
    }
    return render(request, "recipes/write.html", context)


# SUBMITTING VIA A FORM

@login_required    
def update(request, recipe_id=None):
	if request.method == "GET":
		recipe =  get_object_or_404(Recipe, pk=recipe_id)
		initial = recipe.__dict__
		initial['ingredients'] = get_ingredient_list(recipe_id)
		form = InputRecipeForm(initial = initial)
		context = {
			"form" : form,
			"recipe_id" : recipe_id,
		}
		return render(request, "recipes/update.html", context)
		
	else:
		form = InputRecipeForm(request.POST)
		
		if form.is_valid():
			#Remove recipe from cookbook and deal with links
			if recipe_id:
				recipe_id = request.POST.get("recipe_id", None)
				recipe =  get_object_or_404(Recipe, pk=recipe_id)
			
				request.user.cookbook.recipes.remove(recipe)
				if recipe.number_references == 1:
					recipe.delete()
				else :
					recipe.number_references -=1
					recipe.save()
			
			#Add new recipe to cookbook	
			new_recipe = form.save()
			request.user.cookbook.recipes.add(new_recipe)			
			
			return HttpResponseRedirect(reverse("recipes:index")) #TODO : return the new recipe detail
		print(form.errors)
		return write(request, error_message_form="Submitted an invalid form")


# SUBMITTING VIA RECIPE-SCRAPPERS


def scrape(request):
    try:
        scraper = scrape_me(request.POST["url"])
        form = form_from_scrape(scraper)
        context = {'form':form}
        return render(request, "recipes/scrape.html", context)
    except WebsiteNotImplementedError:
        msg = "the url " + request.POST["url"] + " is not supported by recipe_scraper"
        return write(request, error_message_link=msg)


# SEARCHING RECIPES


def search(request):
    if request.method == "GET":
        form = SearchRecipeForm()
        context = {
            "form": form,
            "results": None,
            "has_results": False,
        }
        return render(request, "recipes/search.html", context)
    else:
        form = SearchRecipeForm(request.POST)
        if form.is_valid():
            query = form.search(user = request.user)
            form = SearchRecipeForm(initial=form.cleaned_data)
            context = {
                "form": form,
                "results": query,
                "has_results": True,
            }
            return render(
                request, "recipes/search.html", context
            )  # TODO : look at how we can use a redirection for this.
        print(form.errors)
        return write(request, error_message_form="Submitted an invalid form")

