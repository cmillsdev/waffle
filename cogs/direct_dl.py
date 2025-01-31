import urllib.parse
import requests
import discord
import yt_dlp
import os
import subprocess
import asyncio
import re
from discord.ext import commands
import time
import socketio


class DirectDLCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.download_message = None
        self.sio = socketio.AsyncClient()
        self.last_update_time = 0
        self.update_interval = 2
        self.updating = False

        self.bot.loop.create_task(self.connect_to_socket())

    async def connect_to_socket(self):
        try:
            await self.sio.connect("http://127.0.0.1:42069")
            print("Connected to flask socket")
        except socketio.exceptions.ConnectionError as e:
            print(f"Connection to socket failed: {e}")
    async def download_tiktok_video(self, tiktok_url):
        try:
            ydl_opts = {
                "outtmpl": "tiktok_video.%(ext)s",  # Dynamic filename
                "format": "best",
                "final_ext": "mp4",
                "format_sort": ["filesize:10M"]
                #"quiet": True,  # Suppress yt-dlp output
            }

            loop = asyncio.get_event_loop()
    # Step 1: Make the download function async-compatible
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info (metadata)
                info_dict = await loop.run_in_executor(None, ydl.extract_info, tiktok_url, False)
            
            # Save the video description to a variable
                video_description = info_dict.get('description', None)
            
            # Download the video
                await loop.run_in_executor(None, ydl.download, [tiktok_url])

            # Get the filename from the info_dict
                video_filename = ydl.prepare_filename(info_dict)

            # Return video info
                video_info = {
                    "filename": video_filename,
                    "desc": video_description,
                }
            return video_info
        except Exception as e:
            raise Exception(f"Error downloading TikTok video: {str(e)}")

    # Step 2: Make the video compression function async-compatible
    async def compress_video(self, input_file, output_file):
        try:
            file_size_mb = os.path.getsize(input_file) / (1024 * 1024)
            print(f"Original file size: {file_size_mb:.2f} MB")

            if file_size_mb <= 10:
                return input_file

            ffmpeg_command = [
                "ffmpeg",
                "-i",
                input_file,
                "-c:v",
                "libx264",
                "-vf",
                "scale=576:-1",
                "-crf",
                "32",
                # "-b:v",
                # "5M", 
                "-c:a",
                "aac",
                "-b:a",
                "96k",  # Set audio bitrate to 128kbps
                "-preset",
                "fast",
                output_file,
            ]

            # Use asyncio to run the ffmpeg subprocess in the background
            process = await asyncio.create_subprocess_exec(*ffmpeg_command)
            await process.communicate()  # Wait for the process to finish

            compressed_file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"Compressed file size: {compressed_file_size_mb:.2f} MB")

            if compressed_file_size_mb > 10:
                raise Exception(
                    "Compression failed to reduce the file size under 15MB."
                )

            return output_file
        except Exception as e:
            raise Exception(f"Error compressing video: {str(e)}")

    # Step 4: File deletion should be async-compatible
    async def remove_video_files(self):
        current_dir = os.getcwd()

        # Loop through all files in the current directory
        for file_name in os.listdir(current_dir):
            file_path = os.path.join(current_dir, file_name)

            # Check if it's a .webm or .mp4 file and delete it
            if file_name.endswith('.webm') or file_name.endswith('.mp4'):
                if os.path.isfile(file_path):  # Confirm it's a file, not a directory
                    os.remove(file_path)
                    print(f"Deleted {file_path}")
                else:
                    print(f"{file_path} is not a file, skipping.")

    # Listener to catch messages containing TikTok URLs
    @commands.Cog.listener()
    async def on_message(self, message):
        tiktok_url_pattern = r"(https?://(?:www\.)?(?:vt\.)?tiktok\.com/[^\s]+)"
        instagram_reel_regex = r"(https?://(?:www\.)?instagram\.com/reel/[^\s]+)"
        #youtube_shorts_regex = r"https://(www\.)?youtube\.com/shorts/\w+"
        combined_regex = f"({tiktok_url_pattern})|({instagram_reel_regex})"
        match = re.search(combined_regex, message.content)
        if match:
            # Step 5: Use an async method to get the TikTok link
            link = match.group(0)
            try:
                # Step 6: Download the TikTok video asynchronously
                video_info = await self.download_tiktok_video(link)

                # Step 7: Compress the video to fit under Discord's limit
                compressed_video_filename = "tiktok_video.mp4"
                #compressed_video = await self.compress_video(
                #    video_info["filename"], compressed_video_filename
                #)

                # Step 8: Prepare the video for Discord upload
                file = discord.File(
                    compressed_video_filename, filename=os.path.basename("tiktok_video.mp4")
                )

                await message.delete()
                await message.channel.send(f"<@{message.author.id}>\n>>> {video_info['desc']}", file=file)

                # Step 9: Clean up the local files asynchronously
                # there should be no mp4/webm in the folder
                await self.remove_video_files()

            except Exception as e:
                print(f"Error processing TikTok video: {str(e)}")

    async def update_message(self, message, done=False):
        current_time = time.time()
        if message and self.download_message:
            if current_time - self.last_update_time >= self.update_interval:
                if not self.updating:
                    self.updating = True
                    await self.download_message.edit(content=message)
                    self.last_update_time = current_time
                    self.updating = False
            elif done:
                await self.download_message.edit(content=message)

    async def call_backs(self):
        @self.sio.event
        async def connect():
            print("Connected to the box")

        @self.sio.event
        async def progress_update(data):
            progress = data.get("progress")
            await self.update_message(progress)

        @self.sio.event
        async def download_complete(data):
            message = data.get("message")
            await self.update_message(message, done=True)

        @self.sio.event
        async def download_error(data):
            error_message = data.get("message")
            await self.update_message(error_message)

    @commands.command(name="mdl", description="upload music to music server")
    async def start_download(self, ctx, url):
        await self.call_backs()
        self.download_message = await ctx.reply("Starting download...")

        await self.sio.emit("start_download", {"url": url, "quality": "best"})

        if not self.sio.connected:
            await self.download_message.edit(content="Failed to connect to socket")


async def setup(bot):
    await bot.add_cog(DirectDLCog(bot))
