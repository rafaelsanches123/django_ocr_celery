from django.urls import path

from . import views

urlpatterns = [
  path('', views.HomeView.as_view(), name='home'),
  path('ocr/', views.OcrView.as_view(), name='ocr'),
  path('task/<str:task_id>/', views.TaskView.as_view(), name='task'),
]