from discord.ext import tasks, commands
import discord
from discord import Embed
from bs4 import BeautifulSoup as bs
import re
import helpers.embed
from config import MLCOOKIES
from strings.urls import MLROUNDS_URL, MLSTANDINGS_URL, MLBASE_URL
import json
from rich.console import Console

class MusicLeagueCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.console = Console()

    @commands.command(name='fmd', description='get current round')
    async def mlround(self, ctx):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0"
        }
        try:
            r = await self.bot.ml_httpx_request(MLROUNDS_URL)
            soup = bs(r.text, 'lxml')
            print(soup)
            rounds = [d for d in soup.find_all('div', class_='card')]
            section = rounds[1]
            title = [section.find('span', class_='card-text text-body-tertiary').get_text(strip=True), 
            section.find('h5', class_='card-title').get_text(strip=True)]
        except Exception as e:
            await ctx.reply("oh god the cookie expired! everyone panic!\n", f"```python\n{e}\n```")
            return 0

        linkify_element = section.find('p', class_='card-text')

        if linkify_element:
            x_html_value = linkify_element.get('x-html', '')

            match = re.search(r"linkifyStr\('([^']+)'", x_html_value)
            title.append(match.group(1))
        
        url_section = section.find('div', class_='mt-3')['hx-get']
        url = (MLBASE_URL + url_section)
        r = await self.bot.ml_httpx_request(url)

        sub_soup = bs(r.text, 'lxml')
        
        semibold_spans = sub_soup.find_all('span', class_='fw-semibold')
        sub_status_dic = {"round": title[0], "title": title[1],"description": title[2], "voted": [], "waiting": []}
        
        if len(semibold_spans) >= 2:
            done_section = semibold_spans[0].find_next_sibling('div')
            for user_div in done_section.find_all('div', class_='col-auto'):
                user_title = user_div.find('a')['title']
                sub_status_dic["voted"].append(user_title)

            waiting_section = semibold_spans[1].find_next_sibling('div')
            for user_div in waiting_section.find_all('div', class_='col-auto'):
                user_title = user_div.find('a')['title']
                sub_status_dic["waiting"].append(user_title)

        embed = Embed(title=f"{sub_status_dic['round']}: {sub_status_dic['title']}", description=sub_status_dic['description'])
        embed.add_field(name=f'Waiting For:', value=', '.join(sub_status_dic['waiting']), inline=False)
        embed.add_field(name=f'Done:', value=', '.join(sub_status_dic['voted']), inline=False)
        await ctx.reply(embed=embed)

    @commands.command(aliases=('fmds', 'fmdstandings', 'fmdstanding'), description='Get current standings')
    async def mlstandings(self, ctx):
        r = await self.bot.ml_httpx_request(MLSTANDINGS_URL)
        soup = bs(r.text, 'lxml')
        user_data = {}

        cards = soup.find_all("div", class_="card-body py-3")

        for card in cards:
            username_tag = card.find("div", class_="col text-truncate").find("h5")
            points_tag = card.find("div", class_="col-auto text-body").find("h5")

            if username_tag and points_tag:
                username = username_tag.get_text(strip=True)
                points = int(points_tag.get_text(strip=True))
                user_data[username] = points

        embed = Embed(title='FUCK ME ~~DEAD~~ STANDING$')
        for count, user in enumerate(user_data.keys(), start=1):
            if count == 1:
                award = '🌟'
            elif count == 2:
                award = '⭐'
            elif count == 3:
                award = '✨'
            elif count == len(user_data):
                award = '<:negative:1301293100576014337>'
            else:
                award = ''
            embed.add_field(name=f"{count}. {user} {award}", value=f"{user_data[user]} points", inline=False)

        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(MusicLeagueCog(bot))



