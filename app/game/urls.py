"""
URL mappings for slotmachine API.
"""

from django.urls import path,include

from game import views


urlpatterns = [
    path('slotmachine',views.SlotMachineViewSet.as_view()),
]