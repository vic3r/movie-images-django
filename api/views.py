from django.conf import settings
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from movieimages import settings
from requests.exceptions import HTTPError
import redis
import requests
from http import HTTPStatus

# Connect to our Redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT, db=0)

fetch_movie_url = 'https://www.myapifilms.com/imdb/idIMDB'

class MovieImageAPI(APIView):

  def process_response(self, title_id, value, msg, status):
    response = {
      'title_id': title_id,
      'value': value,
      'msg': msg
    }
    return Response(response, status=status)

  def get(self, request, title_id):
    value = redis_instance.get(title_id)
    if value:
      return self.process_response(title_id, value, 'success', HTTPStatus.OK)
    else:
      try:
        film_uri = f'{fetch_movie_url}?idIMDB={title_id}&token={settings.API_TOKEN}'
        film_response = requests.get(film_uri)
      except HTTPError as http_err:
        return self.process_response(title_id, None, 'Error ocurred', http_err)
      except Exception:
        return self.process_response(title_id, None, 'Internal Server Error', HTTPStatus.INTERNAL_SERVER_ERROR)
      else:
        response = film_response.json()
        try:
          movie_image = response['data']['movies'][0]['urlPoster']
          redis_instance.set(title_id, movie_image)
          return self.process_response(title_id, movie_image, f'{title_id} successfully set', HTTPStatus.OK)
        except Exception:
          return self.process_response(title_id, None, response['error']['message'], HTTPStatus.NOT_FOUND)

class PersonImageAPI(APIView):

  def process_response(self, name, value, msg, status):
    response = {
      'name': name,
      'value': value,
      'msg': msg
    }
    return Response(response, status=status)

  def get(self, request, name):
    name = name.replace("_", " ")
    value = redis_instance.get(name)
    if value:
      return self.process_response(name, value, 'success', HTTPStatus.OK)
    else:
      try:
        film_uri = f'{fetch_movie_url}?name={name}&token={settings.API_TOKEN}'
        film_response = requests.get(film_uri)
      except HTTPError as http_err:
        return self.process_response(name, None, 'Error ocurred', http_err)
      except Exception:
        return self.process_response(name, None, 'Internal Server Error', HTTPStatus.INTERNAL_SERVER_ERROR)
      else:
        response = film_response.json()
        try:
          movie_image = response['data']['names'][0]['urlPhoto']
          redis_instance.set(name, movie_image)
          return self.process_response(name, movie_image, f'{name} successfully set', HTTPStatus.OK)
        except Exception:
          return self.process_response(name, None, response['error']['message'], HTTPStatus.NOT_FOUND)
