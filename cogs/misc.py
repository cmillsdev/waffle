from discord import app_commands
from discord.ext import commands
from random import randint
from loguru import logger
import json
import discord
from utils.db import DB
from utils.embed import twitcher_embed, juiceme
from typing import Literal


class MiscCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("lib/p4-enemy.json", "r", encoding="utf-16") as f:
            self.p4_data = json.load(f)

    @app_commands.command(name="juiceme", description="get relevant community urls")
    async def juiceme(self, interaction: discord.Interaction):
        logger.info(f"{interaction.user} wants to juice")
        await interaction.response.send_message(embed=juiceme())

    @app_commands.command(name="roll", description="Roll a dice")
    async def roll(self, interaction: discord.Interaction, num: int, faces: int):
        """Rolls a die in NdN format."""
        logger.info(f"{interaction.user} rolled {num}d{faces}")
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

    @app_commands.command(name="p4", description="search enemy info for Persona 4")
    async def p4(self, interaction: discord.Interaction, enemy: str):
        results = []
        for key, value in self.p4_data.items():
            if enemy in key or enemy in value:
                results.append(key)
        p4_embed = discord.Embed(title="P4 Resists")
        for x in results:
            # phys, fire, ice, elec, wind, light, dark
            p4_embed.add_field(name=x.key, value=x["resists"])
        p4_embed.add_field(
            name="info",
            value="I'll make this better but\nin this order: phys, fire, ice, elec, wind, light, dark\ns:strong, w:weak, r:repel, n:null, d:drain",
        )
        await interaction.response.send_message(embed=p4_embed)

    @app_commands.command(name="twitchers", description="Get twitcher status")
    async def twitchers(
        self, interaction: discord.Interaction, option: Literal["all", "online"]
    ):
        logger.info(f"{interaction.user} wants twitcher status")
        if option == "all":
            embed = twitcher_embed(await DB().get_twitchers(), False)
        elif option == "online":
            embed = twitcher_embed(await DB().get_twitchers(), True)
        await interaction.response.send_message(embed=embed)

    @commands.command(name="test", description="Test command")
    async def test(self, ctx):
        embed = discord.Embed(title="Test", description="Test")
        file = discord.File("test.mp4", filename="test.mp4")
        await ctx.send(embed=embed, file=file)


async def setup(bot):
    await bot.add_cog(MiscCog(bot))
