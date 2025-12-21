"""
URL configuration for Rassid project.

The urlpatterns list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    
Add an import:  from my_app import views
Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    
Add an import:  from other_app.views import Home
Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    
Import the include() function: from django.urls import include, path
Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from users.views import login_view 
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/airports/", include("airports.urls")),
    path("api/flights/", include("flights.urls")),
    path("api/users/", include("users.urls")),
    path("api/passengers/", include("passengers.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/tickets/", include("tickets.urls")),

    path("platform-admin/", include("platform_admin.urls")),
    path("airport-admin/", include("airports.urls")),
    path("operator/", include("flights.urls")),
    path("passengers/", include("passengers.urls")),
    path("tickets/", include("tickets.urls")),
    path("", include("public.urls")),

    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)