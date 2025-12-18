from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_request, name='signup_request'),
    path('create-operator/', views.create_operator, name='create_operator'),
    path('delete-operator/<int:operator_id>/', views.delete_operator, name='delete_operator'),
    path('logout/', views.logout_view, name='logout'),
]
