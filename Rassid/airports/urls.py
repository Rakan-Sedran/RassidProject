from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/operator/', views.operator_dashboard, name='operator_dashboard'),
    path('dashboard/operator/demo/', views.operator_dashboard, name='operator_dashboard_demo'),
    path('dashboard/admin/', views.admin_dashboard, name='airport_admin_dashboard'),
    path('dashboard/admin/demo/', views.admin_dashboard, name='admin_dashboard_demo'),
    path('update-gate/', views.update_gate, name='update_gate'),
    path('sync-flights/', views.sync_flights, name='sync_flights'),
    path('api/sync/', views.api_sync_flights, name='api_sync_flights'),
]
