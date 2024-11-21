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

    async def httpx_request(self, url, cookies=None):
        cookie = {"app.musicleague.com":"MTczMjEzNTc0N3xMNkNTOURrY2stRTdpMVl5TW81RWFqVGlBVXJKa3RVT01aTjdjM2tWdkVtZGNPMlpiLVAxZmpKazU3bFI2RGdHcXNXaVFCSEpudWJkUldnalFXN3VaTFRoUExHSWFZUUVxSnJXUHAwTWV5RDBWQjU1Sld3X3ZJbkJvbWNlbXVCbTl4LTdwbkhLNmc1Vl9aajJ6NUJ2R3VQR2J2YzZFYnVET2E1Qk9RdzJVX2I2T29ITUk4NzZwQkdreWFhVk5OSEJGMTBwOTJXR2VUUzBLa29XcEtkTFlKdWVKUnVFR1lieW5VWGhHMDhkT1dLQjdsZFBQN25yNGFVLUdrQ19GaVZSMmNzRWJnZ0pCWjBrZ3NsTURRLWtPY0wzdVRFNDJGR3N6RDhOX0RLR09DRVB3ZjNfeDFkVnpKOFdPTnNWQXdVb25DME5kLUgtT1FLY3NPODBLYWNfamh2bWp1eV9MUUVpSEFLd3BUemJsOER0OS1rc0dKRHozaUI4YWttY0RLQUhfM3prN1RzdG9lZ1J5eHg2Ym5FZm9qTE9PdTdGZzRJdVBDQU5kXzhoZ1pJRUdieTZuWXZDd1hRZWJPdVcyaThnT0NiSTYxNlpncUJMajVjUGpOQVRyQTBiZWwyb0xBZ0FfSlYzQXh1aTQ0QlRTNTFNNnZNVnB3SVU2Tmk2VFhwZ1oyU3ZCZ2xmSjZQcjhlUU5pWGZxOU4xaDJTTEN4bjdrOUZyYkhhdzdXdlpveUNxLWt3a1YtUzhQYmNpdUJRdHFCaWVLSTQ2SkQxOGdpckY2S3lROC1ybE1QWDBqSllRMHQxUEdnQVFFenVqOWtuUktIQ2hZZVRoZUFBcUpqQWIwOHhDSWdnLVdaN0lOX3ladEx5ajV0TlhiX3V0b3ZaRExHRm9odFpuRFJXT19qS195X2g2WUJxXzVQRXFHWnNCaEF4VmdRaFJ0cXp0X1RfYzNteEkzanh2NU9XV0NLV1JQa0s4ck85R1VRR2t1ZzRLbWExT3gzZmxpekZqaGxxZ05tdDJiT1JYQ1lMSF9HUT09fF9aE4S1B8g9LqTRsKjhcwymtvZ2gI0zt943vaJAS_Ru"}
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, cookies=cookie)

        return response
