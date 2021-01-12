# -*- coding: utf-8 -*-
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader
from .models import Ingredient, RecipeCategory, RestrictedDiet, Recipe


def index(request):
	latest_recipes_list = Recipe.objects.order_by("-id")[:5]
	template = loader.get_template('recipes/index.html')
	context = {
		'latest_recipes_list': latest_recipes_list,
	}
	return HttpResponse(template.render(context, request))
