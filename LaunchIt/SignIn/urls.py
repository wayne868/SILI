from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('individual-signin/', views.individual_signin, name='individual_signin'),
    path('event-signin/', views.event_signin, name='event_signin'),
    path('reports/', views.monthly_report, name='monthly_report'),
]
