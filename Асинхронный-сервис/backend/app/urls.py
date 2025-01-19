from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/substances/', search_substances),  # GET
    path('api/substances/<int:substance_id>/', get_substance_by_id),  # GET
    path('api/substances/<int:substance_id>/update/', update_substance),  # PUT
    path('api/substances/<int:substance_id>/update_image/', update_substance_image),  # POST
    path('api/substances/<int:substance_id>/delete/', delete_substance),  # DELETE
    path('api/substances/create/', create_substance),  # POST
    path('api/substances/<int:substance_id>/add_to_medicine/', add_substance_to_medicine),  # POST

    # Набор методов для заявок
    path('api/medicines/', search_medicines),  # GET
    path('api/medicines/<int:medicine_id>/', get_medicine_by_id),  # GET
    path('api/medicines/<int:medicine_id>/update/', update_medicine),  # PUT
    path('api/medicines/<int:medicine_id>/update_dose/', update_dose),  # PUT
    path('api/medicines/<int:medicine_id>/update_status_user/', update_status_user),  # PUT
    path('api/medicines/<int:medicine_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/medicines/<int:medicine_id>/delete/', delete_medicine),  # DELETE

    # Набор методов для м-м
    path('api/medicines/<int:medicine_id>/update_substance/<int:substance_id>/', update_substance_in_medicine),  # PUT
    path('api/medicines/<int:medicine_id>/delete_substance/<int:substance_id>/', delete_substance_from_medicine),  # DELETE

    # Набор методов для аутентификации и авторизации
    path("api/users/register/", register),  # POST
    path("api/users/login/", login),  # POST
    path("api/users/logout/", logout),  # POST
    path("api/users/<int:user_id>/update/", update_user)  # PUT
]
