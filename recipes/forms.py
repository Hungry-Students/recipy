# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm, Textarea
from .models import Recipe, Ingredient, IngredientQuantity, RestrictedDiet, Comment

class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'category', 'quantity', 'quantity_unit', 'diets', 'instructions']
        widgets = {
            'instructions': Textarea(attrs={'cols': 80, 'rows': 20}),
            'diets' : forms.CheckboxSelectMultiple,
        }


    def save(self):
        #building new recipe
        r = self.instance
        r.name = self.cleaned_data['name']
        r.instructions = self.cleaned_data['instructions']
        r.quantity = self.cleaned_data['quantity']
        r.quantity_unit = self.cleaned_data['quantity_unit']
        r.save()

        for diet in self.cleaned_data['diets']:
            r.diets.add(diet)

        return r


class CommentForm(forms.ModelForm):
    content = forms.CharField(label ='', widget = forms.Textarea(
        attrs = {
            'class': 'form-control',
            'placeholder': 'Leave a comment!',
            'rows': 4,
            'cols': 50
        }))
    class Meta:
        model = Comment
        fields = ['content']
