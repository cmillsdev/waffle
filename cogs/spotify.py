import spotipy
from config import (
    MUSIC_CHANNEL,
    SPOTIPY_CLIENT_ID,
    SPOTIPY_CLIENT_SECRET,
    SPOTIPY_REDIRECT_URI,
    PLAYLIST_URI,
)
import discord
from discord.ext import commands
from discord import app_commands

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spotify = spotipy.Spotify(
            auth_manager=spotipy.SpotifyOAuth(
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET,
                redirect_uri=SPOTIPY_REDIRECT_URI,
                scope="playlist-modify-public",
                open_browser=False,
                show_dialog=True,
            )
        )
        self.PLAYLIST_URI = PLAYLIST_URI

    @app_commands.command(name="playlist_url", description="Get the playlist URL.")
    async def playlist_url(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "https://open.spotify.com/playlist/6xHdV7jlRcuon1AaUDVvNb?si=e1ae8290dd4247a8",
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        music_channel = await self.bot.fetch_channel(MUSIC_CHANNEL)
        if (
            message.channel.id == music_channel.id
            and "https://open.spotify.com/" in message.content
        ):
            try:
                print(f"Got Spotify link: {message.content}")
                add_tracks = []

                if message.content.startswith("https://open.spotify.com/album/"):
                    album = self.spotify.album(message.content)
                    print(f"Got album: {album['name']}")
                    for track in album["tracks"]["items"]:
                        add_tracks.append(track["uri"])

                elif message.content.startswith("https://open.spotify.com/track/"):
                    track = self.spotify.track(message.content)
                    print(f"Got track: {track['name']}")
                    add_tracks = [track["uri"]]

                # Retrieve the current playlist tracks
                playlist_tracks = self.spotify.playlist_tracks(PLAYLIST_URI)
                existing_uris = {track['track']['uri'] for track in playlist_tracks['items']}

                # Filter out tracks that are already in the playlist
                new_tracks = [track for track in add_tracks if track not in existing_uris]

                if new_tracks:
                    print(f"Adding {len(new_tracks)} new tracks to playlist.")
                    await message.add_reaction("🧇")
                    self.spotify.playlist_add_items(PLAYLIST_URI, new_tracks)
                else:
                    print("No new tracks to add. All tracks already in the playlist.")

            except spotipy.exceptions.SpotifyException as e:
                print(f"SpotifyException: {str(e)}")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
