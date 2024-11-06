from discord.ext import tasks, commands
import discord
import httpx
import helpers.embed
import config
import json
from rich.console import Console

class TasksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alldebrid = bot.debrid
        self.debrid_check.start()
        self.basic_vote_task.start()
        self.console = Console()

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
                    self.console.print_exception(show_locals=True)
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
                        embed = helpers.embed.download_ready(user_id, filename)
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
    

    @tasks.loop(seconds=300)
    async def basic_vote_task(self):
        URL = "https://static01.nyt.com/elections-assets/pages/data/2024-11-05/results-president.json"
        CALLS_URL = "https://static01.nyt.com/elections-assets/pages/data/feeds/f3258ab4-9a8f-42b3-97b7-dce4ae4c8e07/race-calls/2024-11-05.json"
        p_channel = await self.bot.fetch_channel('1263616237603393556')
        async with httpx.AsyncClient() as resp:
            results = await resp.get(URL)
            calls = await resp.get(CALLS_URL)
        results = results.json()
        calls = calls.json()
        races = results['races']
        embed = discord.Embed(title="Current Votes")
        total_total_votes = results['partyControlData']['results'][0]['offices']['P']['votes']
        total_trump_votes = results['partyControlData']['results'][0]['offices']['P']['party_balance']['GOP']['votes']
        total_harris_votes = results['partyControlData']['results'][0]['offices']['P']['party_balance']['DEM']['votes']
        #embed.add_field(name="**TOTALS**", value=f"**H**: {((total_harris_votes/total_total_votes)*100):.2f} | **T**: {((total_trump_votes/total_total_votes)*100):.2f}", inline=False)
        fields = 0
        gop_leads = 0
        dem_leads = 0
        state_calls = [0,0]
        gop_calls = ''
        dem_calls = ''
        for race in races:
            # state_name = race['top_reporting_unit']['name']
            trump_votes = race['top_reporting_unit']['candidates'][0]['votes']['total']
            harris_votes = race['top_reporting_unit']['candidates'][1]['votes']['total']
            
            if harris_votes > trump_votes:
                lead_notifier = 'DEM'
                dem_leads += 1
            else:
                lead_notifier = 'REP'
                gop_leads += 1
        for call in calls['data']:
            if call['office_id'] == 'P':
                if call['party'] == 'Democrat':
                    state_calls[0] += 1
                    dem_calls += f"{call['state_abb']}, "
                elif call['party'] == 'Republican':
                    state_calls[1] += 1
                    gop_calls += f"{call['state_abb']}, "
            # if trump_votes != 0 and harris_votes != 0:
            #     if fields >= 25:
            #         embed.add_field(name=f"{state_name}({lead_notifier})", value=f"**T**: {trump_percent:.2f}% | **H**: {harris_percent:.2f}%\n*Expctd*: {leftover_percent:.2f}%")
            #         fields += 1
            #     else:
            #         fields += 1
            #         embed2.add_field(name=f"{state_name}({lead_notifier})", value=f"**T**: {trump_percent:.2f}% | **H**: {harris_percent:.2f}%\n*Expctd*: {leftover_percent:.2f}%")
        #embed.add_field(name="**TOTALS**", value=f"**H**: {((total_harris_votes/total_total_votes)*100):.2f} | **T**: {((total_trump_votes/total_total_votes)*100):.2f}\n*States*: **H|T**: {dem_leads}|{gop_leads}", inline=False)
        georgia = races[9]
        
        pennsyl = races[42]
        total_votes = pennsyl['top_reporting_unit']['total_expected_vote']
        trump_votes = pennsyl['top_reporting_unit']['candidates'][0]['votes']['total']
        harris_votes = pennsyl['top_reporting_unit']['candidates'][1]['votes']['total']
        trump_percent = (trump_votes / total_votes) * 100
        harris_percent = (harris_votes / total_votes) * 100
        counted_percent = trump_percent + harris_percent
        leftover_percent = 100 - counted_percent
        dem_seats = results['partyControlData']['results'][0]['offices']['P']['party_balance']['DEM']['seats']
        gop_seats = results['partyControlData']['results'][0]['offices']['P']['party_balance']['GOP']['seats']
        embed.add_field(name=f"**HARRIS** ({dem_seats})", value=f"{((total_harris_votes/total_total_votes)*100):.2f}%\n**Vote leads:** {dem_leads}\n**Race Calls:** {state_calls[0]}\n{dem_calls}")
        embed.add_field(name=f"**TRUMP** ({gop_seats})", value=f"{((total_trump_votes/total_total_votes)*100):.2f}%\n**Vote leads:** {gop_leads}\n**Race Calls:** {state_calls[1]}\n{gop_calls}")
        state1_name, state1_value = await build_state_field("pennsylvania", races)
        state2_name, state2_value = await build_state_field("georgia", races)
        embed.add_field(name=state1_name, value=state1_value)
        embed.add_field(name=state2_name, value=state2_value)
        await p_channel.send(embed=embed)
        # if fields > 25:
        #     await p_channel.send(embed=embed2)

    async def build_state_field(self, state_name, races):
        # Find the race for the given state
        state_race = next((race for race in races if race['top_reporting_unit']['name'].lower() == state_name), None)
        if not state_race:
            return None  # Return None if the state is not found in races data

        # Calculate the total expected votes and each candidate's votes
        total_votes = state_race['top_reporting_unit']['total_expected_vote']
        trump_votes = state_race['top_reporting_unit']['candidates'][0]['votes']['total']
        harris_votes = state_race['top_reporting_unit']['candidates'][1]['votes']['total']
        
        # Calculate the vote percentages for each candidate
        trump_percent = (trump_votes / total_votes) * 100 if total_votes > 0 else 0
        harris_percent = (harris_votes / total_votes) * 100 if total_votes > 0 else 0
        counted_percent = trump_percent + harris_percent
        leftover_percent = 100 - counted_percent

        # Create the field data as a dictionary
        field_name = f"__**{state_name}**__"
        field_value = (
            f"**DEM**: {harris_percent:.2f}%\n"
            f"**GOP**: {trump_percent:.2f}%\n"
            f"**Remaining**: {leftover_percent:.2f}%"
        )
        
        # Return as a tuple that can be directly used with embed.add_field
        return field_name, field_value



async def setup(bot):
    await bot.add_cog(TasksCog(bot))
