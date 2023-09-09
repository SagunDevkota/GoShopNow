"""
Django admin customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django import forms
from django.conf import settings
from ckeditor.widgets import CKEditorWidget

from core import models

import os


class ProductAdminForm(forms.ModelForm):
    extra = forms.CharField(label="Build Description", widget=CKEditorWidget(),initial="")

    class Meta:
        model = models.Product
        fields = '__all__'

class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email','first_name','last_name','phone']
    search_fields = ['email']
    fieldsets = (
        (None,{'fields':(
                'first_name',
                'last_name',
                'phone',
                'email',
                'password',
                'reward_points'
                )}),
        (
            _('Permissions'),
            {
                'fields':(
                        'is_active',
                        'is_staff',
                        'is_superuser',
                )
            }
        ),
        (_('Important dates'),{'fields':('last_login',)}),
    )
    readonly_fields = ['last_login','reward_points']
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':(
                'first_name',
                'last_name',
                'email',
                'password1',
                'password2',
                'phone',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )


class ProductAdmin(admin.ModelAdmin):
    """Define admin page for product."""
    ordering = ['p_id']
    list_display = ['p_id','name','price','stock']
    search_fields = ['name']
    fieldsets = (
        (None,{'fields':(
                'name',
                'price',
                'rating',
                )}),
        (
            _('Stocks'),
            {
                'fields':(
                        'stock',
                        'threshold',
                )
            }
        ),
        (_('Description'),{'fields':('description','extra',)}),
        (_('Category'),{'fields':('category',)})
    )
    readonly_fields = ['rating',"description"]
    form = ProductAdminForm

    def save_model(self, request, obj, form, change):
        if obj.p_id:
            try:
                with open(self.get_html_file_path(obj.p_id), 'w') as file:
                    file.write(form.cleaned_data["extra"])
                obj.description = self.get_html_file_url(obj.p_id)  # Set the description field to the file URL
            except FileNotFoundError:
                pass
        else:
            obj.save()
            file_content = form.cleaned_data["extra"]
            self.update_html_file(obj.p_id, file_content)
            obj.description = self.get_html_file_url(obj.p_id)  # Set the description field to the file URL
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['extra'].initial = ""
        if obj and 'extra' in form.base_fields:
            try:
                with open(obj.description, 'r') as file:
                    content = file.read()
                    form.base_fields['extra'].initial = content
            except (FileNotFoundError, AttributeError):
                pass
        
        return form

    def update_html_file(self, p_id, content):
        file_path = self.get_html_file_path(p_id)
        with open(file_path, 'w') as file:
            file.write(content)

    def get_html_file_path(self, p_id):
        return os.path.join(settings.CKEDITOR_FILE_PATH, f'description_{p_id}.html')

    def get_html_file_url(self, p_id):
        file_path = self.get_html_file_path(p_id)
        return os.path.join(settings.CKEDITOR_FILE_PATH, os.path.relpath(file_path, settings.CKEDITOR_FILE_PATH))

class ReviewAdmin(admin.ModelAdmin):
    """Define admin page for review."""
    list_display = ['id','review','user']

class CategoryAdmin(admin.ModelAdmin):
    """Define category page for product."""
    list_display = ['category']

class CartAdmin(admin.ModelAdmin):
    """Define cart page for product purchase."""
    list_display = ['id','p_id','quantity','user']

class PaymentAdmin(admin.ModelAdmin):
    """Define admin panel for payment."""
    list_display = ['id',"quantity","status","user",'date_time']
    readonly_fields = ['date_time']

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super().formfield_for_dbfield(db_field, **kwargs)
        
        # Check if the field has null=True and default=None
        if field and db_field.null and db_field.default is None:
            field.required = False  # Set the field as not required

        return field  
    
class PaymentProductsAdmin(admin.ModelAdmin):
    """Define admin panel for individual product in payment"""
    list_display = ['payment_id','product']
    
class ProductImageAdmin(admin.ModelAdmin):
    """Admin panel for uploading product images"""
    list_display = ['p_id','image_url']
    list_per_page = 50

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Review, ReviewAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Cart, CartAdmin)
admin.site.register(models.Payment, PaymentAdmin)
admin.site.register(models.ProductImage,ProductImageAdmin)
admin.site.register(models.PaymentProduct,PaymentProductsAdmin)