from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для программ
    path('api/programms/', search_programms),  # GET
    path('api/programms/<int:programm_id>/', get_programm_by_id),  # GET
    path('api/programms/<int:programm_id>/update/', update_programm),  # PUT
    path('api/programms/<int:programm_id>/update_image/', update_programm_image),  # POST
    path('api/programms/<int:programm_id>/delete/', delete_programm),  # DELETE
    path('api/programms/create/', create_programm),  # POST
    path('api/programms/<int:programm_id>/add_to_manufacture/', add_programm_to_manufacture),  # POST

    # Набор методов для заявок
    path('api/manufactures/', search_manufactures),  # GET
    path('api/manufactures/<int:manufacture_id>/', get_manufacture_by_id),  # GET
    path('api/manufactures/<int:manufacture_id>/update/', update_manufacture),  # PUT
    path('api/manufactures/<int:manufacture_id>/update_status_user/', update_status_user),  # PUT
    path('api/manufactures/<int:manufacture_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/manufactures/<int:manufacture_id>/delete/', delete_manufacture),  # DELETE

    # Набор методов для м-м
    path('api/manufactures/<int:manufacture_id>/update_programm/<int:programm_id>/', update_programm_in_manufacture),  # PUT
    path('api/manufactures/<int:manufacture_id>/delete_programm/<int:programm_id>/', delete_programm_from_manufacture),  # DELETE

    # Набор методов пользователей
    path('api/users/register/', register), # POST
    path('api/users/login/', login), # POST
    path('api/users/logout/', logout), # POST
    path('api/users/<int:user_id>/update/', update_user) # PUT
]
