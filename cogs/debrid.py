import asyncio
import time
import os
import discord
from discord import app_commands
from discord.ext import commands
from rich import print
from rich.console import Console
from lxml import objectify
import httpx
from bs4 import BeautifulSoup as bs
import config
import helpers.embed
import strings.urls as Urls
import helpers.yar as yar


class DebridCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alldebrid = bot.debrid
        self.console = Console()

    @commands.command(
        name="deletetorrents",
        description="Delete x amount of old torrents.",
        brief="Delete x amount of old torrents.",
    )
    async def deletetorrents(self, ctx, *, num: int):
        async with httpx.AsyncClient() as resp:
            r = await resp.get(Urls.DEBRID_STATUS_READY)
            r = r.json()["data"]["magnets"]

        print(f"{len(r)} torrents cached.")
        mag_slice = []
        for torrent in r:
            mag_slice.append(torrent)
        mag_slice = mag_slice[-num:]
        ids = []
        for torrent in r:
            if torrent in mag_slice:
                ids.append(r[torrent]["id"])
        for i in ids:
            await self.alldebrid.delete_magnet(i)
            time.sleep(0.1)
        print(f"{num} old torrents deleted.")
        await ctx.reply(f"{num} old torrents deleted.")

    @commands.command(
        name="ready",
        description="Returns the number of cached torrents.",
        brief="Returns the number of cached torrents.",
    )
    async def ready(self, ctx):
        r = await self.alldebrid.get_all_magnet_status()
        print(f"{len(r)} cached torrents.")
        await ctx.send(f"{len(r)} torrents.\nThe limit is 1000.")

    @app_commands.command(
        name="magnet",
        description="Upload a magnet directly.",
    )
    async def mag(self, interaction: discord.Interaction, magnet: str):
        if magnet.startswith("magnet"):
            await interaction.response.defer(thinking=True)
            mag = self.alldebrid.upload_magnets(magnet)['data']['magnets'][0]
            print(f"Adding magnet for {mag['name']}")
            ready_list = {'ready':[]}
            if mag['ready']:
                ready_list['ready'].append(mag['name'])
                embed = helpers.embed.download_ready(interaction.user.id, ready_list)
                print(f"{mag['name']} is ready.")
                dl_channel = await self.bot.fetch_channel(config.DL_CHANNEL)
                await dl_channel.send(embed=embed)
                await interaction.followup.send("Download ready and waiting!")
            else:
                #data = [mag[0], "magnet", interaction.user.id, "magnet"]
                await interaction.followup.send("It aint ready.")
        else:
            print(f"Invalid link recv'd: {magnet}")
            await interaction.response.send_message("Not a valid magnet link.")

    @commands.command(
        aliases=('stat', 'status'),
        description="Returns status of active torrents.",
        brief="Returns status of active torrents.",
    )
    async def dl_status(self, ctx):
        allstatus = []
        with open("queue.txt", "r") as f:
            queue = f.readlines()
        queue = [i.strip().split(",") for i in queue]
        for magnet in queue:
            magnet_status = self.alldebrid.get_magnet_status(magnet[0])
            allstatus.append(
                {
                    "filename": magnet_status["data"]["magnets"]["filename"],
                    "size": magnet_status["data"]["magnets"]["size"],
                    "seeders": magnet_status["data"]["magnets"]["seeders"],
                    "speed": magnet_status["data"]["magnets"]["downloadSpeed"],
                    "downloaded": magnet_status["data"]["magnets"]["downloaded"],
                }
            )
        if len(allstatus) <= 0:
            await ctx.send("No active downloads.")
        else:
            try:
                embed = helpers.embed.debrid_status(allstatus)
                await ctx.reply(embed=embed, mention_author=False)
            except Exception as ex:
                print(f"Error Occurred: {ex}")
                await ctx.reply("Error occurred. Try again later.")

    @app_commands.command(
        name="m3u",
        description="Generate a playlist of debrid links for easy streaming in VLC",
    )
    async def m3u_gen(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer(thinking=True)
        print("Generating M3U files for each directory.")
        exclude_files = ["txt", "../", "srt", "nfo", "jpg", "jpeg", "exe", "rar"]
        file_list = []

        async def fetch_directory_content(url):
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                return response.text
        
        async def generate_m3u_for_directory(folder_name, folder_url):
            print(f"Generating M3U for: {folder_name}")
            m3u_name = f"{folder_name}.m3u"
            files = []

            # Fetch and parse the directory content
            html_content = await fetch_directory_content(folder_url)
            soup = bs(html_content, "html.parser")

            # Find all files in this directory, excluding specified types
            for tag in soup.find_all("a"):
                href = tag.get("href")
                if not any(href.endswith(ext) for ext in exclude_files) and not href.endswith("/"):
                    files.append(f"{folder_url}{href}\n")

            # Write this folder's file list to its own .m3u file
            if files:
                with open(f"tmp/{m3u_name}", "w") as f:
                    f.writelines(files)
                file_list.append(f"tmp/{m3u_name}")
                print(f"Added {m3u_name} to file list.")
        
        # Start scanning from the root URL
        async def scan_directory(url, parent_name="root"):
            await generate_m3u_for_directory(parent_name, url)
            
            # Fetch directory content and check for subdirectories
            html_content = await fetch_directory_content(url)
            soup = bs(html_content, "html.parser")
            
            for tag in soup.find_all("a"):
                href = tag.get("href")
                if href.endswith("/") and href not in exclude_files:
                    subfolder_name = href.strip("/")
                    subfolder_url = f"{url}{href}"
                    await scan_directory(subfolder_url, subfolder_name)
        
        # Start the recursive scan from the provided URL
        await scan_directory(url)

        # Send files in batches of 10
        while file_list:
            batch = file_list[:10]
            await interaction.followup.send(files=[discord.File(file) for file in batch])
            
            # Remove files after sending each batch
            for file in batch:
                os.remove(file)
                print(f"Removed {file}")
            file_list = file_list[10:]
        
        print("All M3U files generated, sent, and removed.")

    @commands.command(
        name="search", description="Search for torrents", brief="Search for torrents"
    )
    async def search(self, ctx, *, query: str):  # type: ignore
        try:
            results = yar.jackett_search(query)

            if "error" in results:
                await ctx.send(f"Error: {results['error']}")
                return

            results_embed = helpers.embed.torrent_results(results)

            search_message = await ctx.reply(embed=results_embed)

            try:
                def pick_check(m):
                    return m.author == ctx.author and m.content.startswith(
                        ("!pick", "!Pick", "!search")
                    )
                msg = await self.bot.wait_for("message", check=pick_check, timeout=120)

                picks = yar.eval_pick(msg.content)
                
                if not picks:
                    await ctx.reply(f"Search for `{query}` cancelled.")
                else:
                    ready_list = {"ready":[], "not_ready": []}
                    for magnet_link in (magnets := yar.build_magnet_list(picks, results)):
                        api_response = self.alldebrid.upload_magnets(magnet_link)
                        download = api_response['data']['magnets'][0]
                        if download['ready']:
                            magnet_status = self.alldebrid.get_magnet_status(magnet_id=download["id"])
                            filename = magnet_status['data']['magnets']['filename']
                            ready_list["ready"].append(filename)
                        else:
                            ready_list['not_ready'].append({"name":download['name'], "id":download['id']})

                    status_embed = helpers.embed.status_embed(ready_list)
                    await search_message.edit(embed=status_embed)

                    if ready_list['ready']:
                        embed = helpers.embed.download_ready(ctx.author.id, ready_list)
                        dl_channel = await self.bot.fetch_channel(config.DL_CHANNEL)
                        await dl_channel.send(embed=embed)
                    if ready_list['not_ready']:
                        for download in ready_list['not_ready']:
                            with open("queue.txt", "a") as f:
                                f.write(
                                    f"{download['id']},{ctx.author.id}\n"
                                )
            except asyncio.TimeoutError:
                # await ctx.send("TOO SLOW", mention_author=False)
                # add reaction to previously sent em_result embed
                await ctx.reply("You took too long <:negative:1301293100576014337>")
                # await ctx.send("something broke lol")
            except Exception as e:
                self.console.print_exception(show_locals=True)
                await ctx.reply(f"EXCEPTION!\n {type(e).__name__}")

        except Exception as e:
            error_embed = discord.Embed(
                title="An error occurred",
                description=f"TRY AGAIN\n```python\n{str(e)}```",
                color=discord.Color.red(),
            )
            self.console.print_exception(show_locals=True)
            await ctx.send(embed=error_embed)  # type: ignore

    async def handle_torrent_file(self, torrent_url):
        # xml handling
        # encode query
        # dietpi:9117/api/v2.0/indexers/all/results/torznab/api?apikey=jpz98lz3zfizwgs6vl11fkbcru4tpjbg&t=search&q=
        # file = ['path']
        # file_upload = bot.alldebrid.upload_file(file_paths=file)
        pass

async def setup(bot):
    await bot.add_cog(DebridCog(bot))
