# -*- coding: utf-8 -*-
from django import forms
from django.forms import Form, Textarea, ModelForm
from .models import Recipe, Ingredient, IngredientQuantity, RestrictedDiet, Comment, RecipeCategory

class CustomNumberInput(forms.NumberInput):
	def __init__(self, label, attrs=None):
		self.label = label
		super().__init__(attrs)
				
	def render(self, name, value, attrs = None ,renderer=None):
		r = super().render(name, value, attrs,renderer) + self.label
		return r

class CookTimeWidget(forms.MultiWidget):
	def __init__(self, attrs=None):
		widgets = {
			'hours' : CustomNumberInput('hours', attrs={'size' : 10, 'min_value' : 0, 'initial' : 0}), 
			'minutes' : CustomNumberInput('minutes', attrs={'size' : 10, 'min_value' : 0, 'initial' : 0}),
		}
		super().__init__(widgets, attrs)
	
	def render(self, name, value, attrs = None ,renderer=None):
		hours_render = self.widgets[0].render(name+'_hours', value, attrs, renderer)
		minutes_render = self.widgets[1].render(name+'_minutes', value, attrs, renderer)
		return hours_render+minutes_render
		
	def decompress(self, value):
		if value:
			return [value//60, value%60]
		else:
			return [0,0]
			
class CookTimeField(forms.MultiValueField):
	def __init__(self, **kwargs):
		fields = (forms.IntegerField(required=False, min_value=0), forms.IntegerField(required=False, min_value=0))
		super().__init__(fields=fields, require_all_fields=False, **kwargs)
		
	def compress(self, data_list):
		r=0
		if data_list[0]:
			r+=60*data_list[0]
		if data_list[1]:
			r+=data_list[1]
		return r


class RecipeForm(Form):
	name = forms.CharField(label = 'Name')
	category = forms.ModelChoiceField(RecipeCategory.objects.all(), label = 'Category', required=False)
	quantity = forms.IntegerField(min_value=1, label = 'Yield')
	quantity_unit = forms.CharField(label = 'Yield unit', initial='Servings')
	cook_time = CookTimeField(widget = CookTimeWidget)
	diets = forms.ModelMultipleChoiceField(RestrictedDiet.objects.all(), label = 'Diets', widget = forms.CheckboxSelectMultiple)
	instructions = forms.CharField(label = 'Instructions', widget = Textarea(attrs={'cols': 80, 'rows': 20}))

	'''
	class Meta:
		model = Recipe
		fields = ['name', 'category', 'quantity', 'quantity_unit', 'cook_time', 'diets', 'instructions']
		field_classes = {
			#'cook_time' : CookTimeField
		}
		widgets = {
		    'instructions': Textarea(attrs={'cols': 80, 'rows': 20}),
		    'diets' : forms.CheckboxSelectMultiple,
		}
	'''
	def save(self):
		#building new recipe
		r = Recipe()
		r.name = self.cleaned_data['name']
		r.instructions = self.cleaned_data['instructions']
		r.quantity = self.cleaned_data['quantity']
		r.quantity_unit = self.cleaned_data['quantity_unit']
		print(self.cleaned_data['cook_time'])
		r.cook_time = self.cleaned_data['cook_time']
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
