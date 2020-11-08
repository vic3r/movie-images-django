from django.urls import path
from api import views

urlpatterns = [
  path('movies/<slug:title_id>', views.MovieImageAPI.as_view()),
  path('persons/<slug:name>', views.PersonImageAPI.as_view()),
]
