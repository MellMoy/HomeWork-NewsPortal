from django.urls import path
from . import views

app_name = 'my_subscriptions'

urlpatterns = [
    path('', views.my_subscriptions, name='my_subscriptions'),
]