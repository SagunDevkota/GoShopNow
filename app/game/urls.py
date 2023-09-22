"""
URL mappings for slotmachine API.
"""

from django.urls import path,include

from game import views

app_name="game"

urlpatterns = [
    path('slotmachine',views.SlotMachineViewSet.as_view(),name="slotmachine"),
]