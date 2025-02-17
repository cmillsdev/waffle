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
            cookies = {"app.musicleague.com":"MTczOTgwNTA2MnwyUU8wcXVOdFFPcnd2ZFBnNnN2bmtXTVpTVElYemZkUzItc3B2T0RWLWl5cVZzWXAwWHpqQWFLWDdOTVNZVW9wOGdjZ0NTWjBoNnFsQXl0SUpDRnFZVlhFdUcxald2RjJMNUxSZi1ZUG5BMXdNNUlUUGtNUHRndWx3X1dHdktBRmt1QzQwcTlaR0lJLXVqeXY4dGNTT0JUYjlQQTBmTHpIYVBVR00tRTBMTmNxZkhFajRhNmt3ajNRazFkYlJ2NXJCVFpwMTVRVFhBdHB1UFhqMm1IaWZwa0ttSlB3SFRIclhHTGwxMGlkcGhibHlSOVJRS1ROaDNYNm5POGJ6eVlQX0JXOWdmTU9kZFpfYlk3VG10MWVROGJiaHBHV2FTakx6MWUweUdNWUpQcGZKWW02MjY1bVBJdEVBMGJ0NTl5Q2J6cElBUHUxNjlIc3VUZkoybDY1eFRLNXNYTkwtLWRYMkhWN3hRZDUwZ0FJLWV3REw1bGw2eXkzX1M3bjVNNlJqc2hZODBNbWtqYzR1aXVmOXZDUUpGbUUyYmFvUFFRSWJyNEJtendlblVyTEFCbE1FeEZKMVBCeldGQWZ0TERTeTRSdm5LU1VUTWd1MEk0czBFemNmVFNLc0VycFZpTXdpQndjTl9weHctNFlLQ05IREpRRzZJblJsT3dTUFZRUmxDRG5RZFBxQzJvUUNzcWtoTkpnZGZsTHd0TjdSMFdhS2RobDZsajY5SGk5Z2NSdkxsb0xFaWFlc3cwRmp3bDFIeERDdU1ycjdEdDlHT1FGRkU0MGVNdF9rNEYySnF0VXRYanJMLTVFOVFsN0NHODlQbmphX1RlSVlvTUxRZEJMaXNrSEVBWkNQZTdrMGdjU2NfQ1NlQnJCalNsUXlnbmtIVWNZbkptVHZtZzBadkp1UU9sSjBaY0JBTFZONjd6S0hjVnNvZzRvV1BFY01aUnh3WG1VY0RYbVlLbklaWXdiM3BfS1JJTUczRWhibDRnTzUxNkV0Uk9qcVlEVFJZMXQ2NWNCdmpnczNIU21Ha2xIekdEdVNEaC01SHBtb2tUQVh5dFg0T2k0SENtWEV3PT18D0_r0wOPBmHI9nqpEvH9aESHZ5CagSf67A3nZ6y8i3c="}
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0"
            }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, cookies=cookies, headers=headers)

        return response