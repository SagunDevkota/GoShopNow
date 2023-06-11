"""
Django admin customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models

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
        (_('Description'),{'fields':('description',)}),
        (_('Category'),{'fields':('category',)})
    )
    readonly_fields = ['rating']

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
    list_display = ['id',"quantity","status","user","product"]

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super().formfield_for_dbfield(db_field, **kwargs)
        
        # Check if the field has null=True and default=None
        if field and db_field.null and db_field.default is None:
            field.required = False  # Set the field as not required

        return field  

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Review, ReviewAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Cart, CartAdmin)
admin.site.register(models.Payment, PaymentAdmin)