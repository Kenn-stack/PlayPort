import os
import base64
import requests

from datetime import datetime
from spotipy.oauth2 import SpotifyOAuth

from django.shortcuts import redirect


from dotenv import load_dotenv

load_dotenv(override=True)

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
                        

def create_auth_url():
    return SpotifyOAuth(client_id= client_id,
            client_secret=client_secret,
            redirect_uri=os.getenv('REDIRECT_URI'),
            scope="user-library-read, playlist-read-collaborative")


def refresh_if_expired(request):
    print(request.session['token'])
    expires_at = request.session['token']['expires_at']
    dt_expires_at = datetime.fromtimestamp(expires_at)
    is_expired = (dt_expires_at - datetime.now()).seconds <= 60
    if is_expired:
        print('i come here')
        refresh_token = request.session['token']['refresh_token']
        payload = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        cred_str = f"{client_id}:{client_secret}"
        encoded_cred_str = base64.urlsafe_b64encode(cred_str.encode('ascii')).decode('ascii')
        headers = {"Content_Type": "application/x-www-form-urlencoded",
                   "Authorization": f"Basic {encoded_cred_str}"}
        url = 'https://accounts.spotify.com/api/token'
        token = requests.post(url, data=payload, headers=headers)
        print(token)
        request.session['token'] = token.json()
    return True


def login_required(func):

    def inner(request, *args, **kwargs):
        if 'token' not in request.session:

            return redirect("/api/login")
        
        else:

            refresh_if_expired(request)
            return func(request, *args, **kwargs)

    return inner


