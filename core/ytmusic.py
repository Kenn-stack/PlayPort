import google.oauth2.credentials
import google_auth_oauthlib.flow

from django.urls import reverse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class YTMusic():
  def __init__(self):
    
    self.flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('client_secret.json',
        scopes=['https://www.googleapis.com/auth/youtube'])

    self.flow.redirect_uri = 'http://localhost:8000/api/ytm/redirect'


  def get_auth_url(self):
    authorization_url, state = self.flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',)
    return authorization_url, state
    
  def get_access_token(self, request):
    state = request.session['state']
    redirect_uri = request.build_absolute_uri(reverse('api:ytm_callback'))
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/youtube'],
    state=state)
    flow.redirect_uri = redirect_uri

    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

# Store the credentials in the session.
# ACTION ITEM for developers:
#     Store user's access and refresh tokens in your data store if
#     incorporating this code into your real app.
    credentials = flow.credentials
    request.session['ytm_credentials'] = self.credentials_to_dict(credentials)
    
    
  def credentials_to_dict(self, credentials):
    return {
      'token': credentials.token,
      'refresh_token': credentials.refresh_token,
      'token_uri': credentials.token_uri,
      'client_id': credentials.client_id,
      'client_secret': credentials.client_secret,
      'granted_scopes': credentials.granted_scopes
    }
    
    
  def create_playlist(self, request, title):
    credentials = Credentials(**request.session['ytm_credentials'])
    youtube = build("youtube", "v3", credentials=credentials)
    playlist = youtube.playlists().insert(
      part="snippet,status,id",
      body={
        "snippet": {
            "title": title,
        },
        "status": {
            "privacyStatus": "private"  # or "public" or "unlisted"
        }
      }).execute()
    return playlist['id']
    
    
  def add_track_to_playlist(self, request, query, playlist_id):
    credentials = Credentials(**request.session['ytm_credentials'])
    youtube = build("youtube", "v3", credentials=credentials)
    search_results = youtube.search().list(
      part="id",
      q=query,
      type="video"
      ).execute()
    track_id = search_results['items'][0]['id']['videoId']
    
    youtube.playlistItems().insert(
    part="snippet",
    body={
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {
                "kind": "youtube#video",
                "videoId": track_id
            }
        }
    }).execute()
    
    
    