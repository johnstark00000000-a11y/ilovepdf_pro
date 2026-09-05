from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tool/<str:tool_name>/', views.tool_detail, name='tool_detail'),
    path('process/<str:tool_name>/', views.process_pdf, name='process_pdf'),
]
