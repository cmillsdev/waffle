import discord
from discord.ext import commands
from cogwatch import watch
from rich import print
from alldebrid import AllDebrid
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
