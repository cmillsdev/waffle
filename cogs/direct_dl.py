import urllib.parse
import requests
import discord
import yt_dlp
import os
import subprocess
import asyncio
import re
from discord.ext import commands
import socketio

class DirectDLCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.download_message = None
        self.sio = socketio.AsyncClient()

        self.bot.loop.create_task(self.connect_to_socket())
        await self.call_backs()
    async def connect_to_socket(self):
        try:
            await self.sio.connect("http://127.0.0.1:42069")
            print("Connected to flask socket")
        except socketio.exceptions.ConnectionError as e:
            print(f"Connection to socket failed: {e}")

    # Step 1: Make the download function async-compatible
    async def download_tiktok_video(self, tiktok_url):
        try:
            ydl_opts = {
                'outtmpl': 'tiktok_video.%(ext)s',  # Save as tiktok_video.mp4
                'format': 'bestvideo+bestaudio/best',
                'final_ext': 'mp4'
            }
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Use asyncio to avoid blocking
                await loop.run_in_executor(None, ydl.download, [tiktok_url])
            video_filename = 'tiktok_video.mp4'
            converted_video_filename = 'tiktok_video.webm'  # Make sure the file is saved as mp4
            return video_filename
        except Exception as e:
            raise Exception(f"Error downloading TikTok video: {str(e)}")
    
    # Step 2: Make the video compression function async-compatible
    async def compress_video(self, input_file, output_file):
        try:
            file_size_mb = os.path.getsize(input_file) / (1024 * 1024)
            print(f"Original file size: {file_size_mb:.2f} MB")
            
            if file_size_mb <= 15:
                return input_file
            
            ffmpeg_command = [
                "ffmpeg", "-i", input_file,
		        "-c:v", "libvpx",
                "-vf", "scale=-2:720",  # Rescale to max height of 720 while keeping aspect ratio
                "-b:v", "1M",  # Set video bitrate to 1Mbps for compression
		        "-c:a", "libvorbis",
                "-b:a", "128k",  # Set audio bitrate to 128kbps
                "-maxrate", "1M",  # Limit max bitrate
                "-bufsize", "2M",  # Buffer size
                output_file
            ]

            # Use asyncio to run the ffmpeg subprocess in the background
            process = await asyncio.create_subprocess_exec(*ffmpeg_command)
            await process.communicate()  # Wait for the process to finish

            compressed_file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"Compressed file size: {compressed_file_size_mb:.2f} MB")
            
            if compressed_file_size_mb > 15:
                raise Exception("Compression failed to reduce the file size under 15MB.")
            
            return output_file
        except Exception as e:
            raise Exception(f"Error compressing video: {str(e)}")
    
    # Step 4: File deletion should be async-compatible
    async def delete_local_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"File {file_path} not found, cannot delete.")

    # Listener to catch messages containing TikTok URLs
    @commands.Cog.listener()
    async def on_message(self, message):
        tiktok_url_pattern = r"(https?://(?:www\.)?tiktok\.com/[^\s]+)"
        match = re.search(tiktok_url_pattern, message.content)
        if match:
            # Step 5: Use an async method to get the TikTok link
            link = match.group(0)
            try:
                # Step 6: Download the TikTok video asynchronously
                video_filename = await self.download_tiktok_video(link)
                    
                # Step 7: Compress the video to fit under Discord's limit
                compressed_video_filename = 'compressed_tiktok_video.webm'
                compressed_video = await self.compress_video(video_filename, compressed_video_filename)

                # Step 8: Prepare the video for Discord upload
                file = discord.File(compressed_video, filename=os.path.basename(compressed_video))

                await message.delete()
                await message.channel.send(
                    f"<@{message.author.id}>\n", file=file
                )

                    # Step 9: Clean up the local files asynchronously

                await self.delete_local_file(video_filename)
                await self.delete_local_file(compressed_video)

            except Exception as e:
                print(f"Error processing TikTok video: {str(e)}")

    async def update_message(self, message):
        if message and download_message:
            await self.download_message.edit(message)
    
    async def call_backs(self):
        @self.sio.event
        async def connect():
            print('Connect to the box')
        @self.sio.event
        async def progress_update(data):
            progress = data.get('progress')
            print("progress")
            self.update_message(progress)
        @self.sio.event
        async def download_complete(data):
            print("complete")
            message = data.get('message')
            self.update_message(message)
        @self.sio.event
        async def download_error(data):
            print("error")
            error_message = data.get('message')
            self.update_message(message)

    @commands.command(name="mdl", description="upload music to music server")
    async def start_download(self, ctx, url):
        self.download_message = await ctx.reply("Starting download...")

        await sio.emit('start_download', {'url': url, 'quality': 'best'})

        if not sio.connected:
            await self.download_message.edit(content="Failed to connect to socket")
       

async def setup(bot):
    await bot.add_cog(DirectDLCog(bot))
