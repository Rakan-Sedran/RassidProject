from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='platform_admin_dashboard'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
    path('dashboard/demo/', views.dashboard, name='super_admin_demo'),
]
