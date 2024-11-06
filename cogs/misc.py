from discord import app_commands
from discord.ext import commands
from random import randint
import discord
import strings.urls as Urls
from bs4 import BeautifulSoup
import httpx


class MiscCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="waffle",
        description="Receive a random image from a forgotten time, from a forgotten place.",
    )
    async def waffle(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        print("Image requested: waffle")
        async with httpx.AsyncClient() as resp:
            r = await resp.get(Urls.WAFFLE_URL)
        image = BeautifulSoup(r.text, "html.parser").find("img").attrs["src"]
        print(image)
        await interaction.followup.send(Urls.WAFFLE_URL + image)

    @app_commands.command(name="roll", description="Roll a dice")
    async def roll(
        self, interaction: discord.Interaction, num: int, faces: int
    ):
        """Rolls a die in NdN format."""
        print(f"{interaction.user} rolled {num}d{faces}")
        rolls = []
        for i in range(num):
            rolls.append(randint(1, faces))
        if len(rolls) == 1:
            await interaction.response.send_message(f"You rolled a {rolls[0]}")
        elif len(rolls) > 1:
            await interaction.response.send_message(
                f"You rolled {rolls} = {sum(rolls)}"
            )
        else:
            await interaction.response.send_message("Invalid input")

    @commands.command(name="inspireme", description="Get inspiration")
    async def inspireme(self, ctx):
        async with httpx.AsyncClient() as resp:
            r = await resp.get("https://inspirobot.me/api?generate=true")

        await ctx.send(r.text)

    # @commands.command(name="tmnt", description="TMNT logo gen")
    # async def tmnt(self, ctx):
    #     with httpx.AsyncClient() as resp:
    #         r = await resp.get("http://glench.com/tmnt/#"+str(ctx.message.content[6:]).replace(" ", "_"))
    #     await ctx.send(r.text)


async def setup(bot):
    await bot.add_cog(MiscCog(bot))
