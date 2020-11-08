from django.urls import path
from api import views

urlpatterns = [
  path('<slug:title>', views.MovieImageAPI.as_view()),
]
