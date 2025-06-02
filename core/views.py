import os
import spotipy
import requests
import json

from django.shortcuts import redirect, render
from django.urls import reverse
from ninja import NinjaAPI
from ninja.errors import AuthenticationError
from typing import List

from .utils import login_required, spotify_oauth
from .schemas import ExtractedPlaylist, TrackItems
from .ytmusic import YTMusic

from dotenv import load_dotenv

from spotipy.oauth2 import SpotifyOAuth

load_dotenv(override = True)

api = NinjaAPI(urls_namespace='api')

"""spotify_oauth = SpotifyOAuth(
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            redirect_uri=os.getenv('REDIRECT_URI'),
            scope="user-library-read, playlist-read-collaborative")
            
""" 

@api.get("/home")
def index(request):
  return render(request, 'index.html')

"""
The login view gets creates a spotify authorization url and redirects the user to that url to grant permissions. 
"""
@api.get("/spot/login")
def spot_login(request):
  print('i don land')
  auth_url = spotify_oauth.get_authorize_url()
  print(auth_url)
  return redirect(auth_url)

"""
The user is redirected to this view after accepting or rejecting request for authorization. If the user accepts, Spotify sends an authorization code that can be used to request for access and refresh tokens. This function requests for the access tokens and stores them in a session.
"""
@api.get("/spot/redirect")
def spot_callback(request, code, error = None):
  if error:
    raise AuthenticationError
  credentials = spotify_oauth.get_access_token(code)
  request.session['spot_credentials'] = credentials
  return redirect(reverse('api:spot_my_playlists'))


"""
A function to get and display all saved playlists.
"""
@api.get("spot/my-playlists")
@login_required
def spot_my_playlists(request):
  access_token = request.session['spot_credentials']['access_token']
  spotify = spotipy.Spotify(auth=access_token, oauth_manager=spotify_oauth)
  results = spotify.current_user_playlists()
  my_playlists = ExtractedPlaylist(**results).dict()['items']
  playlists = []
  for playlist in my_playlists:
    content = {
        'name': playlist['name'],
        'id': playlist['id'],
        'image_url': playlist['images'][0]['url'],
        'total_tracks': playlist['tracks']['total']
      }
    playlists.append(content)
    
    request.session[playlist['id']] = content
  
  return render(request, 'playlists.html', {'playlists': playlists})
  
  
  
"""
YTMusic
"""
@api.post('/ytm/login')
def ytm_login(request):
  selected_playlists = request.POST.getlist("items")
  request.session['selected_playlists'] = selected_playlists
  ytmusic = YTMusic()
  auth_url, state = ytmusic.get_auth_url()
  request.session['state'] = state
  return redirect(auth_url)
  
  
@api.get('/ytm/redirect')
def ytm_callback(request):
  ytmusic = YTMusic()
  ytmusic.get_access_token(request)
  return redirect(reverse('api:ytm_create_playlist'))
    
    
@api.get('/ytm/create-playlist')
def ytm_create_playlist(request):
  ytmusic = YTMusic()
  selected_playlists = request.session['selected_playlists']
  access_token = request.session['spot_credentials']['access_token']
  spotify = spotipy.Spotify(auth=access_token, oauth_manager=spotify_oauth)
  playlists = []
  for playlist_id in selected_playlists:
    results = spotify.playlist_items(playlist_id)
    playlist_detail = TrackItems(**results).dict()
    track_list = playlist_detail['items']
    playlist_title = request.session[playlist_id]['name']
    new_playlist_id = ytmusic.create_playlist(request, playlist_title)
    for track in track_list:
      data = track['track']['artists']
      flattened_data = [d['name'] for d in data]
      artist = ' ft '.join(flattened_data)
      name = track['track']['name']
      query = f"{name} by {artist}"
      ytmusic.add_track_to_playlist(request, query, new_playlist_id)
      
  return render(request, 'alert.html')
    
    
  
    