import discord
from discord.ext import commands
from cogwatch import watch
from rich import print
from alldebrid import AllDebrid
import httpx
import config
# MY_GUILD = discord.Object(id=1196061028706951279)


class Waffle(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!", description="waffle", intents=discord.Intents.all()
        )
        self.debrid = AllDebrid(apikey=config.DEBRID_KEY)

    @watch(path="cogs", preload=True)
    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="8=====D~~"))

        print(
            f"\n\n[green]Logged in as: {self.user.name} - {self.user.id}\nVersion: {discord.__version__}\n[/]"
        )
    async def on_message(self, message):
        if message.author.bot:
            return

        await self.process_commands(message)

    async def ml_httpx_request(self, url, cookies=None, headers=None):
        if not headers and not cookies:
            cookies = {"app.musicleague.com":"MTczODgxMzIwOXx5ZzJQVnVEOFBINTRELUZWM01sWC1SVzdnUXBpTkYxWlAtOU0wXzJEdUhLSlhSU2JpaDBNczhZSzBzc1V4UHc4RWYxT0pNSnBlcVFfTWRSa2pjX2p6LVFTQ3N6bGVyQzUxMkxzcjRLU2tuY3dKdXBnMG1MSHE5VVJKdVpXZUJCeXJtaXI2endtSW9IekcyR243NHVqOHJOUkJiS1ktNUlwcDV3WVEzM0FMWVV3MXVkU3IteS1aVUpBRXk2VW00MHl4ankwOVc0QmlLV1NrRGdBWW1OT3BDdzhhZGZLT1RsM0F3dlRPQkRZaDNISzhFdzJqMVp4bXA5XzFtUkVtbUNqNWNib1RJWlpNSDNwa1c5amRZMmh6Qmd1WU05UHB2SlBvUjZ2d3BxNldBRUxYSU5CUTlQc2FXTWJxLTdCNFB0c0YyOXlkbWhnMnVwNTd1YVlrNnVmdGE2MmNhVWprQVRsbzRZWUhOQjFYdXVxVUszOWFhUUUyMW5paGk2OTlVYm5IalpKQm9zV3g2MXJTaHh4eV9nQzlOT2dKaTdIQjIwLWZ2LW1CQ21tQWFNbVZIRDBEYkw3bDR0UEZzV0lrNG9tLTlLZUdPZ2JwblgxRDVXcm5BcU8zLXFOa1V3RzBJUjFyR2JWYUJHSjQxQ29jMmJWQm5CQzRCRHk5cUdVYUNNY3ZrU1A1R2xGYnZGNWRmSEk0cU9DYzJkcF81R3oxUTJIZlN6MWFZYmpYRHpXNWh1QjR4Ynd0ZUtxM3NqaDdnbVVjZHNhZ3M0NnBPa0pBS0RXak9GbXRMWlZfRWk2RmlidkVrT3FXTk9IbHJFUU1sN2RGZVZXbDVic2FEQllwSnB6ZXZuR1Q2Tk5GOHhpNUVlUGVNNTJWZVhoRjdyVWRvWGlrZ2VHVTRFbG5McFpGWHZVRE8zNkpRUldva2hUVVNoLXl3dm9JTUxRZlZ4SDU3dTRlMEpBSTBaWnVrTUg3bFlBMjJHUTgxc0Q5cjJxUXZUelZBb1QzZktuN3JWOTZPSU9CaEoyai10UTNqZmZQcENVSTZMWFpYLU0tdm9NbVZsdWpuMlJoTGdfWjgyUDZRNlNDQT09fJ3nvbamij4doRE7ZMhcxyH86JQd4FaCrMgifvKTA1hz"}
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0"
            }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, cookies=cookies, headers=headers)

        return response
