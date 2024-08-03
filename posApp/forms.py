# # forms.py
# from django import forms
# from .models import Products, Category

# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Products
#         fields = ['code', 'category_id', 'name', 'description', 'price', 'quantity', 'status', 'low_quantity_threshold', 'image']
#         widgets = {
#             'image': forms.ClearableFileInput(attrs={'multiple': True}),
#         }
