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
            cookies = {"app.musicleague.com":"MTczNTk0MTc0NnxmNTlTNDBQUTV3TzRtWlpyNVVoLWZTd2d0ZnVELVlpWlZ2YTRzSkdPY0NOaFBDNGhTV2RLMWp2MmgzajhZSVJBVHgwRkJpcV9KNUNNZEJ6VFd6REIwUkEwRHZUeHB5TnFqWFpEeU1YTUJNcnNVNnNrYTc0RnRSSURGVVhyNkhDMnFud0hzbk5nWWtXbXJuRWdTazBUTzdGQWJtQ1Y0M3p2YWlySjhmRkdhOV9wdGxWX05RVUk1Zk4tSHd5N0JPcEdyZm9hY2lmN0Jqd1J0RXp0bS1IYWpDazlxV1VHdjdCeUs4SGVwTkRXN2hJYXVGU0VXcXl3dlJYLTZyZnNnNVJkUGRGZDF4RGFydVlEak9TMXZtdEdRZ3c2X080czNqRmFZLUo4U1NuSlZlMDhRLUpNMVFKQWdnQ1VaeUtoVFItWjdzV1VzSmRYb3dHejh6R0wwMjZKb1VsYlRseTJlVklYd1FhUXhQ…lpBTVVGNzZ2THdMOExwNTFFUi1kQWZlbGVKMUhTN1FEVndzeFpWMkFqaU93YWJqZC1xdmhueDJNUlAwdXEzZDZqYnYxWjV0Q1ZTc1BfNE8wRDFZdXRvUVBreHR5V0NwZGZTcHdzdEVJakZteWxhWTNpd20tOEk2VWdyUWE3NGNVbjFvS1o0UHFscnJ0eUhqbU8wNDhiZHVvUm5WcGdoR1JRSnZEaE0tSXg5czFTSTVoREs3aWExd2xkbHJla1kxcDZobjVBcHRaTmJCWXZVWW5ZOXFOZ2tZUGxFTlBIVnNLR1BxVXktOUl4TkJmenVkVzltNzZtS1lETXduUmtoWHRSclUxRXNTVVc1TzljVzlVek01OEVlOTlZdHFIdEtsMGJSaGpveDFpZlpncWtaZEI2SU9DMXQ4eDNPbFdBenBveWdXYzVUZ0VlWXdhRWFoZ0wwcG5yWUNpVnpldz09fJWRpxYb0Jonckb1tMI9WQfkRJy10B4gInFa5wyOXp-l"}
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0"
            }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, cookies=cookies, headers=headers)

        return response
