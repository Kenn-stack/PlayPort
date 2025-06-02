import os
import base64
import requests

from functools import wraps
from datetime import datetime
from spotipy.oauth2 import SpotifyOAuth


from django.shortcuts import redirect


from dotenv import load_dotenv

load_dotenv(override=True)

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_uri= os.getenv('REDIRECT_URI')
                        

spotify_oauth = SpotifyOAuth(
                client_id= client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope="user-library-read, playlist-read-collaborative")


def refresh_if_expired(request):
  
    expires_at = request.session['spot_credentials']['expires_at']
    dt_expires_at = datetime.fromtimestamp(expires_at)
    is_expired = (dt_expires_at - datetime.now()).total_seconds() <= 60
    if is_expired:
        refresh_token = request.session['spot_credentials']['refresh_token']
        credentials = spotify_oauth.refresh_access_token(refresh_token)
        
        request.session['spot_credentials'] = credentials
    return True


def login_required(func):
  @wraps(func)
  def inner(request, *args, **kwargs):
      if 'spot_credentials' not in request.session:

          return redirect(reverse('api:spot_login'))
      
      else:

          refresh_if_expired(request)
          return func(request, *args, **kwargs)
  return inner
  
  

