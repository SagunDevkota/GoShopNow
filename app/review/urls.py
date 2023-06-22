"""
URL mappings for product API.
"""

from django.urls import path,include

from rest_framework.routers import DefaultRouter

from review import views


router = DefaultRouter()
router.register('review',views.ReviewViewSet)

app_name = 'review' #name for reverse url

urlpatterns = [
    path('',include(router.urls)),
]