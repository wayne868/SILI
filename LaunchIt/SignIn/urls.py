from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('individual-signin/', views.individual_signin, name='individual_signin'),
    path('event-signin/', views.event_signin, name='event_signin'),
    path('reports/', views.monthly_report, name='monthly_report'),
    path('manage-signins/', views.manage_signins, name='manage_signins'),
    # Admin authentication routes
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
]
