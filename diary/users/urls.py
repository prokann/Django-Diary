from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('register_user/', views.register_user, name='register_user'),
    path('profile/', views.profile, name='profile'),

    path('remove_user', views.remove_user, name="remove_user"),

    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('edit_email/', views.edit_email, name='edit_email'),

    path('new_goal', views.unhide_div, name="unhide_div"),
    path('add_goal', views.add_goal, name="add_goal"),
    path('notify_off', views.notify_off, name="notify_off"),
    path('notify_on', views.notify_on, name="notify_on"),
    path('close_goal', views.close_goal, name="close_goal"),
    path('edit_goal', views.edit_goal, name="edit_goal"),
    path('delete_goal', views.delete_goal, name="delete_goal"),

    path('telegram/', views.telegram, name='telegram'),
]