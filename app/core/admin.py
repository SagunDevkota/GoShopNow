"""
Django admin customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django import forms
from django.conf import settings
from ckeditor.widgets import CKEditorWidget
from admincharts.admin import AdminChartMixin
from admincharts.utils import months_between_dates
from django.db.models import F
from elasticsearch_dsl import Index

from core.documents import ProductDocument
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
                'reward_points',
                'token'
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
                'token'
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
                obj.description = self.get_html_file_url(obj.p_id)
            except FileNotFoundError:
                pass
        else:
            obj.save()
            file_content = form.cleaned_data["extra"]
            self.update_html_file(obj.p_id, file_content)
            obj.description = self.get_html_file_url(obj.p_id)
        super().save_model(request, obj, form, change)
        image_url = models.ProductImage.objects.filter(p_id=obj).first()
        if(image_url):
            image_url = image_url.image_url.url
        else:
            image_url = ''
        product_document = ProductDocument(
            meta={'id': obj.p_id},
            p_id=obj.p_id,
            name=obj.name,
            price=obj.price,
            rating=obj.rating,
            category=obj.category.category, 
            stock=obj.stock,
            threshold=obj.threshold,
            description=obj.description,
            image_url=image_url
        )

        product_document.save()

        product_document_index = Index('product')
        product_document_index.refresh()

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
    list_display = ['id','p_id','review','user']
    readonly_fields = ['product_name','user']
    search_fields = ['p_id__name']
    def product_name(self,obj):
        return obj.p_id.name

class CategoryAdmin(admin.ModelAdmin):
    """Define category page for product."""
    list_display = ['category']
    search_fields = ['category']

class CartAdmin(admin.ModelAdmin):
    """Define cart page for product purchase."""
    list_display = ['id','p_id','quantity','user']
    search_fields = ['user__first_name','user__email']

class PaymentAdmin(AdminChartMixin,admin.ModelAdmin):
    """Define admin panel for payment."""
    list_display = ['id',"quantity","status","user",'date_time']
    readonly_fields = ['date_time']
    list_filter = ['date_time']
    ordering = ['-date_time']
    search_fields = ['id']
    start_date = None
    end_date = None

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super().formfield_for_dbfield(db_field, **kwargs)
        
        # Check if the field has null=True and default=None
        if field and db_field.null and db_field.default is None:
            field.required = False  # Set the field as not required

        return field  
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if self.start_date and self.end_date:
            qs = qs.filter(date_time__range=[self.start_date, self.end_date])
        return qs
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['date_form'] = True
        if 'start_date' in request.GET and 'end_date' in request.GET:
            self.start_date = request.GET['start_date'] 
            self.end_date = request.GET['end_date']

        return super().changelist_view(request, extra_context=extra_context)

    def get_list_chart_data(self, queryset):
        if not queryset:
            return {}

        earliest = min([x.date_time for x in queryset])
        now = max([x.date_time for x in queryset])

        labels = []
        totals = []
        name_of_chart = "Hero products by number of sales."
        for b in months_between_dates(earliest, now):
            labels.append(b.strftime("%b %Y"))
            total_revenue = 0
            for x in queryset:
                if(x.date_time.year == b.year and x.date_time.month == b.month):
                    if(x.status == "Completed"):
                        if(x.amount):
                            total_revenue+=x.amount
            
            totals.append(total_revenue)

        return {
            "labels": labels,
            "datasets": [
                {"label": "Total Revenue", "data": totals, "backgroundColor": "#79aec8"},
            ],
            "name_of_chart":"Total Revenue"
        }
    
    
class PaymentProductsAdmin(AdminChartMixin,admin.ModelAdmin):
    """Define admin panel for individual product in payment"""
    fields = ['payment_id','product','product_name','quantity','amount','date']
    list_display = ['payment_id','product']
    list_filter = ['payment_id__date_time']
    readonly_fields = ['product_name',"date"]
    ordering = ['payment_id__date_time']
    search_fields = ['payment_id__id']
    start_date = None
    end_date = None

    def product_name(self, obj):
        return obj.product.name
    
    def date(self,obj):
        return obj.payment_id.date_time

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            product_name=F('product__name')
            )
        if self.start_date and self.end_date:
            qs = qs.filter(
                payment_id__date_time__range=[self.start_date, self.end_date]  
            )

        return qs
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['date_form'] = True
        if 'start_date' in request.GET and 'end_date' in request.GET:
            self.start_date = request.GET['start_date'] 
            self.end_date = request.GET['end_date']

        return super().changelist_view(request, extra_context=extra_context)

    def get_list_chart_data(self, queryset):
        if not queryset:
            return {}

        label_total = {}
        name_of_chart = "Hero products by number of sales."
        for x in queryset:
            if(x.product.name not in label_total.keys()):
                label_total[x.product.name] = x.quantity
            else:
                label_total[x.product.name] += x.quantity
        return {
            "labels": list(label_total.keys()),
            "datasets": [
                {"label": "Total sales unit of product", "data": list(label_total.values()), "backgroundColor": "#79aec8"},
            ],
            "name_of_chart": name_of_chart
        }
    
class ProductImageAdmin(admin.ModelAdmin):
    """Admin panel for uploading product images"""
    list_display = ['p_id','image_url']
    list_per_page = 50

class DeliveryAddressAdmin(admin.ModelAdmin):
    """Admin panel for uploading product images"""
    list_display = ['user']
    list_per_page = 50

class AddressAdmin(admin.ModelAdmin):
    """Admin panel for uploading product images"""
    list_display = ['id','name','parent']
    list_per_page = 50

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Review, ReviewAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Cart, CartAdmin)
admin.site.register(models.Payment, PaymentAdmin)
admin.site.register(models.ProductImage,ProductImageAdmin)
admin.site.register(models.PaymentProduct,PaymentProductsAdmin)
admin.site.register(models.DeliveryAddress,DeliveryAddressAdmin)
admin.site.register(models.Address,AddressAdmin)