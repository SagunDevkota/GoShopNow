"""
Database Models
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self,email, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email address.")
        user = self.model(email=self.normalize_email(email),**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, **extra_field):
        """Create and return a new superuser."""
        user = self.create_user(email=email,
                                **extra_field)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user
    

class User(AbstractBaseUser, PermissionsMixin):
    """Define user model."""
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    reward_points = models.IntegerField(default=0)

    objects = UserManager()

    USERNAME_FIELD = 'email'

class Category(models.Model):
    """Create Category Table"""
    category = models.CharField(max_length=50,primary_key=True)

class Product(models.Model):
    """Create Product Table."""
    p_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    price = models.FloatField()
    threshold = models.IntegerField(validators=[MinValueValidator(0)])
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    rating = models.FloatField(validators=[MinValueValidator(1.0,"Minimum value muct be 1"),MaxValueValidator(5.0,"Maximum value must be 5")],default=0)
    description = models.CharField(max_length=200,default=None,null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='category_product'
    )
    

class Review(models.Model):
    """Create Review Table."""
    p_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_id_review'
    )
    review = models.CharField(max_length=500,default=None,null=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_review'
    )
    rating = models.FloatField(validators=[MinValueValidator(1.0,"Minimum value muct be 1"),MaxValueValidator(5.0,"Maximum value must be 5")],null=True,default=None)

    class Meta:
        unique_together = ('p_id','user')

class Cart(models.Model):
    """Create Cart model."""
    p_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_id_cart'
    )
    quantity = models.IntegerField()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_cart'
    )


class DiscountCoupon(models.Model):
    """Discount coupon for a user."""
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    coupon_code = models.CharField(max_length=6,unique=True)
    max_amount = models.FloatField()
    max_percentage = models.IntegerField()
    used = models.BooleanField(default=False)

class Payment(models.Model):
    TYPE_STATUS = [
        ("Completed", "Completed"),
        ("Pending", "Pending (Default)"),
        ("Refunded", "Refunded")
    ]
    id = models.CharField(max_length=25, primary_key=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(choices=TYPE_STATUS,max_length=9,default='Pending')
    transaction_id = models.CharField(max_length=25,null=True,default=None)
    amount = models.FloatField(default=None,null=True,blank=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_payment"
    )
    date_time = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey(DiscountCoupon,on_delete=models.DO_NOTHING,null=True,default=None)
    discount_amount = models.FloatField(null=True,default=0)

class Address(models.Model):
    """Available addresses."""
    id = models.CharField(max_length=10,unique=True,primary_key=True)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,blank=True,null=True)

    def __str__(self):
        return self.name

class DeliveryAddress(models.Model):
    """User's address"""
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    provience = models.ForeignKey(Address,on_delete=models.CASCADE,related_name='provience_address')
    city = models.ForeignKey(Address,on_delete=models.CASCADE,related_name='city_address')
    area = models.ForeignKey(Address,on_delete=models.CASCADE,related_name='area_address')

class PaymentProduct(models.Model):
    """Products in each payment."""
    payment_id = models.ForeignKey(Payment,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.DO_NOTHING,related_name='product_payment')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    amount = models.FloatField()

class ProductImage(models.Model):
    """Model to store images of product."""
    p_id = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='product_id_image')
    image_url = models.ImageField(upload_to='images/')

    def clean(self):
        # Count the existing records with the same p_id
        existing_images_count = ProductImage.objects.filter(p_id=self.p_id).count()

        # Validate if the count exceeds the limit (5)
        if existing_images_count >= 5:
            raise ValidationError(
                {'p_id': _('Maximum 5 images allowed per product.')}
            )

    def save(self, *args, **kwargs):
        # Clean the model before saving to validate the limit
        self.clean()
        super().save(*args, **kwargs)