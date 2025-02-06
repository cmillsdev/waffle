from discord.ext import tasks, commands
import discord
import httpx
import helpers.embed
import config
import json
import datetime
from rich.console import Console

utc = datetime.timezone.utc

# If no tzinfo is given then UTC is assumed.
times = [
    datetime.time(hour=8, tzinfo=utc)
]

class TasksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alldebrid = bot.debrid
        self.debrid_check.start()
        self.trump_countdown.start()
        self.console = Console()

    @tasks.loop(time=times)
    async def trump_countdown(self):
        politics_channel = await self.bot.fetch_channel(1263616237603393556)
        trump_out_of_office = 1863590400
        now = datetime.datetime.now()

        # Convert the Unix timestamp to a datetime object
        end_of_suffering = datetime.datetime.fromtimestamp(trump_out_of_office)

        # Calculate the difference between now and the timestamp
        time_left = now - end_of_suffering

        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        await politics_channel.send(f"Time left until Dipshit-in-charge fucks off:\n {days} days, {hours} hours, {minutes} minutes, {seconds} seconds")

    @tasks.loop(seconds=30)
    async def debrid_check(self):
        # await self.twitch_check()

        with open("queue.txt", "r") as f:
            queue = f.readlines()
        queue = [i.strip().split(",") for i in queue]
        print(queue)
        if len(queue) > 0:
           for dl_id, user_id in queue:
                try:
                    async with httpx.AsyncClient() as resp:
                        # Make a request to get the status of the magnet download
                        status = self.alldebrid.get_magnet_status(dl_id)
                except Exception as e:
                    print(f"Error getting status for magnet ID {dl_id}: {e}")
                    self.console.print("Magnet ID not found, deleting.")
                    with open("queue.txt", "w") as f:
                            for i in queue:
                                if i[0] != dl_id:  # Write back only the entries that don't match the current dl_id
                                    f.write(f"{i[0]},{i[1]}\n")
                    continue  # Skip to the next item in the queue if there's an error
                
                # Process the status response
                try:
                    # Check if there's an error or if the download status code is greater than 4 (finished or failed)
                    if (
                        status["status"] != "success" 
                        or status["data"]["magnets"]["statusCode"] > 4
                    ):
                        # Rewrite the queue without the completed or errored magnet ID
                        with open("queue.txt", "w") as f:
                            for i in queue:
                                if i[0] != dl_id:  # Write back only the entries that don't match the current dl_id
                                    f.write(f"{i[0]},{i[1]}\n")
                        print(f"Magnet ID {dl_id} removed from the queue.")
                    elif "Ready" in status["data"]["magnets"]["status"]:
                        with open("queue.txt", "w") as f:
                            for i in queue:
                                if i[0] != dl_id:  # Write back only the entries that don't match the current dl_id
                                    f.write(f"{i[0]},{i[1]}\n")
                        print(f"Magnet ID {dl_id} removed from the queue.")
                        filename = status["data"]["magnets"]["filename"]
                        embed = helpers.embed.download_ready_from_queue(user_id, filename)
                        print(f"Removed: {dl_id}")
                        dl_channel = await self.bot.fetch_channel(config.DL_CHANNEL)
                        await dl_channel.send(embed=embed)
                except KeyError as e:
                    print(f"Missing expected key in response for magnet ID {dl_id}: {e}")
                    self.console.print_exception(show_locals=True)
                    continue  # Skip to the next item if there's an issue with the response
                    
                except Exception as e:
                    self.console.print_exception(show_locals=True)
                    pass
                
async def setup(bot):
    await bot.add_cog(TasksCog(bot))
