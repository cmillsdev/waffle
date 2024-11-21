import os
from dotenv import load_dotenv

load_dotenv()

# Discord bot settings
DISCORD_APPID = os.environ["DISCORD_APPID"]
DISCORD_PUBKEY = os.environ["DISCORD_PUBKEY"]
BOT_NAME = os.environ["BOT_NAME"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
DISCORD_OAUTH_ID = os.environ["DISCORD_OAUTH_ID"]
DISCORD_OAUTH_SECRET = os.environ["DISCORD_OAUTH_SECRET"]
DL_CHANNEL = os.environ["DL_CHANNEL"]
MUSIC_CHANNEL = os.environ["MUSIC_CHANNEL"]
# debrid settings
DEBRID_KEY = os.environ["DEBRID_KEY"]
DEBRID_WEBDAV = os.environ["DEBRID_WEBDAV"]
# fortnite settings
FORTNITE_API_KEY = os.environ["FORTNITE_API_KEY"]
# MUSIC_API = os.environ["music_ip"]
WAFFLE_EMOJI = "\N{WAFFLE}"

# Spotify settings
SPOTIPY_CLIENT_ID = os.environ["SPOTIPY_CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]
SPOTIPY_REDIRECT_URI = os.environ["SPOTIPY_REDIRECT_URI"]
PLAYLIST_URI = os.environ["PLAYLIST_URI"]

#music league
MLCOOKIES = os.environ["MLCOOKIE"]
IGNORE_CHANNELS = os.environ["IGNORE_CHANNELS"].split(",")
for i in range(len(IGNORE_CHANNELS)):
    IGNORE_CHANNELS[i] = int(IGNORE_CHANNELS[i])