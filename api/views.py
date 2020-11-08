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

  def process_response(self, title, value, msg, status):
    response = {
      'title': title,
      'value': value,
      'msg': msg
    }
    return Response(response, status=status)

  def get(self, request, title):
    title = title.replace("_", " ")
    value = redis_instance.get(title)
    if value:
      return self.process_response(title, value, 'success', HTTPStatus.OK)
    else:
      try:
        film_uri = f'{fetch_movie_url}?title={title}&token={settings.API_TOKEN}'
        film_response = requests.get(film_uri)
      except HTTPError as http_err:
        return self.process_response(title, None, 'Error ocurred', http_err)
      except Exception:
        return self.process_response(title, None, 'Internal Server Error', HTTPStatus.INTERNAL_SERVER_ERROR)
      else:
        response = film_response.json()
        try:
          movie_image = response['data']['movies'][0]['urlPoster']
          redis_instance.set(title, movie_image)
          return self.process_response(title, movie_image, f'{title} successfully set', HTTPStatus.OK)
        except Exception:
          return self.process_response(title, None, response['error']['message'], HTTPStatus.NOT_FOUND)
