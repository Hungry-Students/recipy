# -*- coding: utf-8 -*-
import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms import Form, Textarea  # , ModelForm
from django.utils.translation import gettext_lazy as _

from .models import (
    Comment,
    Ingredient,
    IngredientQuantity,
    Recipe,
    RecipeCategory,
    RestrictedDiet,
)
from .parser import IngredientParser  # , YieldsParser


class CustomNumberInput(forms.NumberInput):
    def __init__(self, label, attrs=None):
        self.label = label
        super().__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        rendered = super().render(name, value, attrs, renderer) + self.label
        return rendered


class CookTimeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = {
            "hours": CustomNumberInput(
                "hours", attrs={"size": 10, "min_value": 0, "initial": 0}
            ),
            "minutes": CustomNumberInput(
                "minutes", attrs={"size": 10, "min_value": 0, "initial": 0}
            ),
        }
        super().__init__(widgets, attrs)

    def render(self, name, value, attrs=None, renderer=None):
    	value = self.decompress(value)
    	hours_render = self.widgets[0].render(name + "_hours", value[0], attrs, renderer)
    	minutes_render = self.widgets[1].render(name + "_minutes", value[1], attrs, renderer)
    	return hours_render + minutes_render

    def decompress(self, value):
        if value:
            return [value // 60, value % 60]
        else:
            return [None, None]


class CookTimeField(forms.MultiValueField):
    widget = CookTimeWidget

    def __init__(self, **kwargs):
        fields = (
            forms.IntegerField(required=False, min_value=0),
            forms.IntegerField(required=False, min_value=0),
        )
        super().__init__(fields=fields, require_all_fields=False, **kwargs)

    def compress(self, data_list):
        total_time = 0
        if data_list:
            if data_list[0]:
                total_time += 60 * data_list[0]
            if data_list[1]:
                total_time += data_list[1]
            return total_time
        return None  # note : if no input at all, empty data_list is passed


class IngredientObject:
    """Used to easily work with all informations concerning 1 ingredient"""

    def __init__(self, name="", quantity=None, quantity_unit=None, exclude=False):
        self.name = name
        self.quantity = quantity
        self.quantity_unit = quantity_unit
        self.exclude = exclude

        self.quantity_formatted = ""
        self.exclude_formatted = ""
        self.format()

    def format(self):
        # updates the _format values assuming python values may have been changed
        self.quantity_formatted = ""
        if self.quantity:
            self.quantity_formatted += str(self.quantity)
        if self.quantity_unit:
            self.quantity_formatted += str(self.quantity_unit)
        if self.exclude:
            self.exclude_formatted = "checked"
        else:
            self.exclude_formatted = ""
        return self
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.quantity == other.quantity and self.quantity_unit == other.quantity_unit and self.exclude == other.exclude
       	return False
        
 
        
def get_ingredient_list(recipe_id = None):
	"""Gives a list of IngredientObject given a recipe id"""
	recipe = Recipe.objects.get(id=recipe_id)
	if recipe:
		answer=[]
		for ingredientobject in recipe.ingredientquantity_set.all():
			answer.append(IngredientObject(name=ingredientobject.ingredient, quantity=ingredientobject.quantity, quantity_unit=ingredientobject.quantity_unit))
		return answer
	else:
		return None


class IngredientsWidget(forms.Widget):
    template_name = "recipes/snippets/ingredients_widget_template.html"

    def value_from_datadict(self, data, files, name):
        return_list = []
        for elem in data.keys():
            match = re.search(name + "_(?P<id>[0-9]+)_name", elem)
            if match is not None:
                ingredient_id = match.group("id")
                ingredient_name = data[
                    elem
                ].lower()  # Note: we enforce lower case here for ingredient name
                # Note : we keep ingredient even if name is empty, in part for validators to check for errors in the form, so future implementation must be defensive of this fact.

                parser = IngredientParser()
                quantity, quantity_unit = parser.parse_quantity(
                    data.get(name + "_" + ingredient_id + "_quantity", "")
                )

                exclude = bool(data.get(name + "_exclude_" + ingredient_id, None))

                return_list.append(
                    IngredientObject(
                        name=ingredient_name,
                        quantity=quantity,
                        quantity_unit=quantity_unit,
                        exclude=exclude,
                    )
                )
        return return_list

    def format_value(self, value):
        # We keep an object that will be handled by the template
        if value:
            return [ingredient.format() for ingredient in value]
        return [
            IngredientObject()
        ]  # If no initial value is provided, add an empty input spot


class IngredientsField(forms.Field):
    widget = IngredientsWidget

    def __init__(self, empty_value=None, display_type=0, **kwargs):
        self.empty_value = empty_value
        self.display_type = display_type  # can be 0 for input, or 1 for search
        super().__init__(**kwargs)

    def to_python(self, value):
        if value is not None:
            return value  # we already have python values
        else:
            return []

    def widget_attrs(self, widget):
        return {
            "ingredient_list": Ingredient.objects.order_by("name"),
            "display_type": self.display_type,
        }


def validate_no_duplicate(value_list):
    unique_value_list = []
    for e in value_list:
        if e.name in unique_value_list:
            raise ValidationError(
                _("%(ingredient_name) has been listed twice"),
                params={"ingredient_name": e.name},
            )
        unique_value_list.append(e.name)


def validate_non_empty_name(value_list):
    for e in value_list:
        if (e.quantity or e.quantity_unit) and not e.name:
            raise ValidationError(
                _("You have included an ingredient without name"),
                params={},
            )


class InputRecipeForm(Form):
    """ A form designed for recipe input, i.e. new recipes or modification of existing recipes"""

    name = forms.CharField(label="Name", required=True)
    quantity = forms.IntegerField(min_value=1, label="Yield")
    quantity_unit = forms.CharField(label="Yield unit", initial="Servings")
    category = forms.ModelChoiceField(
        RecipeCategory.objects.all(), label="Category", required=False
    )
    cook_time = CookTimeField(required=False)
    diets = forms.ModelMultipleChoiceField(
        RestrictedDiet.objects.all(),
        label="Diets",
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    instructions = forms.CharField(
        label="Instructions", widget=Textarea(attrs={"cols": 80, "rows": 20})
    )
    ingredients = IngredientsField(
        label="Ingredients",
        required=False,
        display_type=0,
        validators=[validate_no_duplicate, validate_non_empty_name],
    )

    def save(self):
        """builds a new recipe and saves it to DB. TODO : manage cookbook links, if recipe is modified manage possible deletion of former recipe"""
        recipe = Recipe()
        recipe.name = self.cleaned_data["name"]
        recipe.instructions = self.cleaned_data["instructions"]
        recipe.quantity = self.cleaned_data["quantity"]
        recipe.quantity_unit = self.cleaned_data["quantity_unit"]
        recipe.cook_time = self.cleaned_data["cook_time"]
        recipe.save()

        for diet in self.cleaned_data["diets"]:
            recipe.diets.add(diet)

        for ingredient in self.cleaned_data["ingredients"]:
            if ingredient.name:  # do not save empty ingredients.
                add_ingredient(
                    recipe,
                    ingredient.name,
                    ingredient.quantity,
                    ingredient.quantity_unit,
                )

        return recipe


class SearchRecipeForm(Form):
    name = forms.CharField(label="Name", required=False)
    category = forms.ModelChoiceField(
        RecipeCategory.objects.all(), label="Category", required=False
    )
    diets = forms.ModelMultipleChoiceField(
        RestrictedDiet.objects.all(),
        label="Diets",
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    ingredients = IngredientsField(
        label="Ingredients",
        required=False,
        display_type=1,
        validators=[validate_no_duplicate],
    )

    def search(self):
        # filtering name
        query = Recipe.objects.filter(name__icontains=self.cleaned_data["name"])
        # filtering category
        if self.cleaned_data["category"]:
            query = query.filter(category__name=self.cleaned_data["category"])
        # filtering diet
        for diet in self.cleaned_data["diets"]:
            query = query.filter(diets__name=diet)
        # filtering ingredients
        for ingredient in self.cleaned_data["ingredients"]:
            if ingredient.name:  # we don't filter for empty inputs
                if ingredient.exclude:
                    query = query.exclude(ingredients__name=ingredient.name)
                else:
                    query = query.filter(ingredients__name=ingredient.name)
        return query


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label="",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Leave a comment!",
                "rows": 4,
                "cols": 50,
            }
        ),
    )

    class Meta:
        model = Comment
        fields = ["content"]


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
