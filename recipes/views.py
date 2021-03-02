# -*- coding: utf-8 -*-
# import re

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect  # , HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from recipe_scrapers import WebsiteNotImplementedError, scrape_me

from users.models import User
from users.utils import is_following

from .forms import CommentForm, InputRecipeForm, SearchRecipeForm
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
    print(cookbook_count)
    if cookbook_count == 1:
        the_one_cookbook = Cookbook.objects.all()[0]
        the_one_user = the_one_cookbook.owner
        return redirect("recipes:cookbook", username=the_one_user.username)
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
    return render(request, "recipes/cookbook/cookbook.html", context)


@login_required
def my_cookbook(request):
    """
    Show the cookbook of request.user
    """
    username = request.user.username
    return redirect("recipes:cookbook", username=username)


def entry(request, entry_id, username):
    """
    Show the entry (=recipe) "entry_id" in user "username"'s cookbook
    """
    user = get_object_or_404(User, username=username)
    cur_entry = get_object_or_404(Entry, id=entry_id)
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


def handle_form(request):
    form = InputRecipeForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse("recipes:index"))
    print(form.errors)
    return write(request, error_message_form="Submitted an invalid form")


# SUBMITTING VIA RECIPE-SCRAPPERS


def scrape(request):
    try:
        existing_recipes = Recipe.objects.filter(url=request.POST["url"])
        if not existing_recipes:
            scraper = scrape_me(request.POST["url"])
            yields_parser = YieldsParser()
            yields_parser.parse(scraper.yields())
            print(scraper.total_time())
            new_recipe = Recipe(
                name=scraper.title(),
                instruction=scraper.instructions(),
                quantity=yields_parser.yields,
                quantity_unit=yields_parser.yields_unit.lower(),
                url=request.POST["url"],
            )
            new_recipe.save()
            ingredient_parser = IngredientParser()
            for e in scraper.ingredients():
                ingredient_parser.parse(e.lower())
                # NOTE: we force lower case in the argument, upper case will be
                # given in the parser when needed (e.g. cL)
                add_ingredient(
                    new_recipe,
                    ingredient_parser.ingredient_name,
                    ingredient_parser.quantity,
                    ingredient_parser.quantity_unit,
                )
        else:
            return write(
                request,
                error_message_link="this recipe already exists",
                existing_recipe=existing_recipes[0],
            )
        return HttpResponseRedirect(reverse("recipes:index"))
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
            query = form.search()
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


# Non view functions


def add_ingredient(
    recipe, ingredient_name, ingredient_quantity, ingredient_quantity_unit
):
    # Fetching or creating ingredient
    possible_ing_obj = Ingredient.objects.filter(name=ingredient_name)
    if possible_ing_obj:
        ingredient_object = possible_ing_obj[0]
    else:
        ingredient_object = Ingredient(name=ingredient_name)
        ingredient_object.save()

    # Building relation to recipe
    relation = IngredientQuantity(
        recipe=recipe,
        ingredient=ingredient_object,
        quantity=ingredient_quantity,
        quantity_unit=ingredient_quantity_unit,
    )
    relation.save()
