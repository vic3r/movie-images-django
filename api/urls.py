from django.urls import path
from api import views

urlpatterns = [
  path('<slug:title_id>', views.MovieImageAPI.as_view()),
]
