"""
URL configuration for Rassid project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Frontend Pages
    path('', include('public.urls')),
    path('passengers/', include('passengers.urls')),
    path('airports/', include('airports.urls')),
    path('platform/', include('platform_admin.urls')),
    path('users/', include('users.urls')),

    # API Endpoints (Keeping existing structure if needed, or commenting out if duplicates)
    # path("api/airports/", include("airports.urls")), 
    # path("api/flights/", include("flights.urls")),
]
