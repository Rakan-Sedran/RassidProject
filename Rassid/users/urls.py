from django.urls import path
from .views import LoginView, UserListView

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("all/", UserListView.as_view()),
]
