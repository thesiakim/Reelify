from django.urls import path
from . import views

app_name = 'reelbots'
urlpatterns = [
    path('', views.run_chatbot, name='run_chatbot'),
]
