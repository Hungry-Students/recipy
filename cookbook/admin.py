# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Cookbook, Entry

admin.site.register(Cookbook)
admin.site.register(Entry)
