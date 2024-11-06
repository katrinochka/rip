from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('programms/<int:programm_id>/', programm_details, name="programm_details"),
    path('programms/<int:programm_id>/add_to_manufacture/', add_programm_to_draft_manufacture, name="add_programm_to_draft_manufacture"),
    path('manufactures/<int:manufacture_id>/delete/', delete_manufacture, name="delete_manufacture"),
    path('manufactures/<int:manufacture_id>/', manufacture)
]
