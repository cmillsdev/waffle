import urllib.parse
import requests
import discord
import yt_dlp
import os
import subprocess
import asyncio
import re
from discord.ext import commands

class DirectDLCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        print('tikkytokky')
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

    @commands.command(name="mdl", description="upload music to music server")
    async def start_download(self, ctx, url):
        FLASK_API_URL = "http://192.168.1.238:42069/start_download"
        FLASK_WS_URL = "ws://192.168.1.238:42069/socket.io/"
        #response = requests.get(f"http://192.168.1.238:42069/start_download", params={'url': url})

        # if response.status_code == 200:
        #     result = response.json()
        #     await ctx.reply(f"Download started successfully: {result.get('message', 'No message')}")
        # else:
        #     error = response.json().get('error', 'Unknown error occurred.')
        #     await ctx.reply(f"Error: {error}")
        message = await ctx.reply("Starting download...")

        # Call Flask API to initiate the download
        response = requests.get(FLASK_API_URL, params={'url': url, 'quality': 'best'})
        if response.status_code != 200:
            await message.edit(content="Failed to start download.")
            return

        # Now connect to WebSocket to receive progress updates
        async with websockets.connect(FLASK_WS_URL) as ws:
            await ws.send('{"event": "start_download", "data": {"url": url}}')
            try:
                async for msg in ws:
                    data = json.loads(msg)
                    if data.get('progress_update'):
                        await message.edit(content=f"Progress: {data['progress_update']['progress']}")
                    elif data.get('download_complete'):
                        await message.edit(content="Download completed!")
                        break
                    elif data.get('download_error'):
                        await message.edit(content=f"Error: {data['download_error']['message']}")
                        break
            except Exception as e:
                await message.edit(content=f"Error during WebSocket connection: {str(e)}")


async def setup(bot):
    await bot.add_cog(DirectDLCog(bot))
