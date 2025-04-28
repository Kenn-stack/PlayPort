import os
import spotipy
import requests

from django.shortcuts import redirect, render
from ninja import NinjaAPI
from ninja.errors import AuthenticationError

from .utils import create_auth_url, refresh_if_expired, login_required

from dotenv import load_dotenv

from spotipy.oauth2 import SpotifyOAuth

load_dotenv(override = True)

api = NinjaAPI()

"""
The login view gets creates a spotify authorization url and redirects the user to that url to grant permissions. 
"""
@api.get("/login")
def login(request):
# if request.session['token']:
#     return render(request, 'playlist.html')
  auth_url = create_auth_url().get_authorize_url()
  return redirect(auth_url)

"""
The user is redirected to this view after accepting or rejecting request for authorization. If the user accepts, Spotify sends an authorization code that can be used to request for access and refresh tokens. This gunction requests for the access tokens and stores them in a session.
"""
@api.get("/redirect")
def callback(request, code, error = None):
  if error:
    raise AuthenticationError
  token = create_auth_url().get_access_token(code)
  print(token)
  request.session['token'] = token
  return redirect("/api/my-saved-playlists")


"""
A function to get and display all saved playlists.
"""
@api.get("/my-saved-playlists")
@login_required
def my_playlists(request):
  access_token = request.session['token']['access_token']
  url = "https://api.spotify.com/v1/me/playlists"
  headers = {
  'Authorization': f'Bearer {
    access_token
  }'
}
  my_saved_playlists = requests.get(url, headers = headers)
  return my_saved_playlists.json()