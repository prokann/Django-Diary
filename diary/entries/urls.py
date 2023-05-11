from django.urls import path
from . import views


urlpatterns = [
    path('all_notes/', views.all_notes, name="all_notes"),
    path('new_note/', views.new_note, name="new_note"),
    path('statistics/', views.statistics, name="statistics"),

    path('save_list', views.save_list, name="save_list"),
    path('will_did_case', views.will_did_case, name="will_did_case"),
    # path('edit_list', views.edit_list, name="edit_list"),
    path('delete_case', views.delete_case, name="delete_case"),
    path('delete_list', views.delete_list, name="delete_list"),

    path('write_note', views.write_note, name="write_note"),
    path('edit_note', views.edit_note, name="edit_note"),
    path('delete_note', views.delete_note, name="delete_note"),

    path('download_data', views.download_data, name="download_data"),

    # path('mood_images', mood_images, name='mood_images'),


    # path('filter_date', views.filter_date, name="filter_date"),
    # path('show_notices', views.show_notices, name="show_notices"),

]