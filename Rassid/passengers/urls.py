from django.urls import path
from . import views

urlpatterns = [
    path('tracking/', views.tracking, name='tracking'),
    path('tracking/<int:flight_id>/', views.tracking, name='tracking_detail'),
]
