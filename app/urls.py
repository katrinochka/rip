from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('programms/<int:programm_id>/', programm),
    path('manufactures/<int:manufacture_id>/', manufacture),
]