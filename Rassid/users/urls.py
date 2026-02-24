from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Password reset URLs
    path('password_reset/',
        views.CustomPasswordResetView.as_view(),
        name='password_reset'),
    path('password_reset/done/',
        views.CustomPasswordResetDoneView.as_view(),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
        views.CustomPasswordResetConfirmView.as_view(),
        name='password_reset_confirm'),
    path('reset/done/',
        views.CustomPasswordResetCompleteView.as_view(),
        name='password_reset_complete'),
]