from flask import Flask, redirect, request, session, url_for
import requests
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = "44197ssg098h0235nabov"

# Spotify API credentials
CLIENT_ID = "ddb5b22c77174fe38c335d965865861c"
CLIENT_SECRET = "c85b658cd3274b73b7c73fac17319ba7"
REDIRECT_URI = "http://127.0.0.1:5000/callback"
SCOPE = "user-top-read user-read-recently-played"

sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)

@app.route("/")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for("summary"))

@app.route("/summary")
def summary():
    token_info = session.get("token_info", None)
    if not token_info:
        return redirect(url_for("login"))

    access_token = token_info["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Fetch top tracks
    top_tracks = requests.get(
        "https://api.spotify.com/v1/me/top/tracks?time_range=medium_term&limit=5", headers=headers
    ).json()

    # Fetch recently played tracks
    recently_played = requests.get(
        "https://api.spotify.com/v1/me/player/recently-played?limit=5", headers=headers
    ).json()

    # Generate summary
    summary = "<h1>User's Listening History</h1><h2>Top Tracks:</h2><ul>"
    for item in top_tracks["items"]:
        summary += f"<li>{item['name']} by {item['artists'][0]['name']}</li>"
    summary += "</ul><h2>Recently Played:</h2><ul>"
    for item in recently_played["items"]:
        track = item["track"]
        summary += f"<li>{track['name']} by {track['artists'][0]['name']}</li>"
    summary += "</ul>"

    return summary

if __name__ == "__main__":
    app.run(debug=True)
