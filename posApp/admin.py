from django.contrib import admin
from posApp.models import Category, Products, Sales, SalesItems

# Register your models here.
admin.site.register(Category)
admin.site.register(Products)
admin.site.register(Sales)
admin.site.register(SalesItems)
# admin.site.register(Employees)
