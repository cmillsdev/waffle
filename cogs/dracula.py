from random import randint
from discord.ext import commands
from discord import app_commands, Interaction
import httpx

message_count = 0
pause_count = 0


class ButtCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chance = 2
        self.pause_count = 0

    async def get_phrase(self):
        async with httpx.AsyncClient() as resp:
            r = await resp.get("http://127.0.0.1:42069/random_phrase")
            
        return r.json()["phrase"][:2000]
     # Slash command to add a phrase with an ephemeral response
    @app_commands.command(name="addphrase", description="Add a new phrase to the database")
    async def add_phrase(self, interaction: Interaction, phrase: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://127.0.0.1:42069/discord_add_phrase", json={"phrase": phrase}
            )
        await interaction.response.send_message("Added!", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.bot.user in message.mentions:
            await message.reply(await self.get_phrase())

        if "roll tide" in message.content.lower():
            print(f"Roll tide detected in {message.content}")
            await message.channel.send("Roll tide!")
        else:
            chatty = True
            if chatty == True:
                if not (message.content.startswith("!") or "https://" in message.content):
                    if randint(1, 100) <= self.chance and self.pause_count == 0:
                        new_message = await self.get_phrase()

                        if new_message != message.content:
                            self.pause_count = randint(1, 10)
                            await message.channel.send(new_message)
                    else:
                        if self.pause_count > 0:
                            self.pause_count -= 1


async def setup(bot):
    await bot.add_cog(ButtCog(bot))
