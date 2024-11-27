import discord
from discord.ext import commands
import json
import os
from collections import defaultdict


def load_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return {}


def filter_quests_with_status_2(quests):
    return {quest["qid"] for quest in quests if quest["status"] == 2}


def extract_quest_info(quests, location_mapping):
    quest_info = {}
    for quest_id, quest_data in quests.items():
        quest_name = quest_data.get("QuestName", "Unknown Quest")
        location_id = quest_data.get("location", "any")
        location = location_mapping.get(location_id, "???")
        quest_info[quest_id] = {"QuestName": quest_name, "Location": location}
    return quest_info


def load_tarkov_users():
    try:
        with open("tarkov-users.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def load_altrecipes():
    try:
        with open("strings/recipes.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_tarkov_users(data):
    with open("tarkov-users.json", "w") as f:
        json.dump(data, f, indent=4)


# Function to find the correct JSON profile based on the Tarkov username
def find_profile_by_username(
    tarkov_name, profiles_folder="/home/cody/fika/user/profiles/"
):
    for filename in os.listdir(profiles_folder):
        if filename.endswith(".json"):
            with open(os.path.join(profiles_folder, filename), "r") as f:
                profile_data = json.load(f)
                if (
                    profile_data.get("info", {}).get("username").lower()
                    == tarkov_name.lower()
                ):
                    return filename  # Return the filename if a match is found
    return None  # Return None if no match is found


def get_user_profile(user, profiles_folder="/home/cody/fika/user/profiles/"):
    tarkov_users = load_tarkov_users()
    if tarkov_users:
        file = tarkov_users[user]["file"]
        with open(os.path.join(profiles_folder, file), "r") as f:
            profile_data = json.load(f)

        return profile_data


def calculate_skill_levels(skills):
    skill_dict = {}
    for skill in skills:
        level = 0
        points_required = 10  # Starting with level 1 requirement
        progress = skill["Progress"]
        while progress >= points_required:
            progress -= points_required
            level += 1
            points_required = min(
                100, 10 + (level * 10)
            )  # Increase by 10, capped at 100
        skill_dict[skill["Id"]] = level

    return skill_dict  # Return level and remaining points toward the next level


class TarkovCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tarkov_users = load_tarkov_users()

    @commands.command(name="tarkov", description="Some tarky commands!")
    async def link(self, ctx, *, tarkov_nick):
        discord_id = str(ctx.user.id)
        profile_file = find_profile_by_username(tarkov_nick)
        if profile_file:
            self.tarkov_users[discord_id] = {
                "tarkov_nick": tarkov_nick,
                "file": profile_file,
            }
            save_tarkov_users(self.tarkov_users)
            await ctx.reply(
                f"{ctx.user.mention}, your Tarkov username has been linked as {tarkov_nick} (profile: {profile_file})."
            )
        else:
            await ctx.reply(
                f"{ctx.user.mention}, no matching profile was found for {tarkov_nick}. Please check the username and try again."
            )

    @commands.command(name="altrecipes", description="get your alt recipes")
    async def altrecipes(self, ctx, *, user=None):
        recipes = load_altrecipes()
        query = ctx.message.content.split()[1:]
        query = " ".join(query)
        if "," in query:
            query = query.split(",")
        else:
            query = [query]

        embed = discord.Embed(title="Alt Recipes")
        for recipe in query:
            recipe = recipe.strip().title()
            if recipe in recipes:
                r = recipes[recipe]
                embed.add_field(
                    name=f"({r['score']}) {r['name']}",
                    value=f"**{r['tier']}**\nPower: {r['power']}\n Items: {r['items']}\n Buildings: {r['buildings']}\n Resources: {r['resources']}\n Resources\*: {r['resources_scaled']}\n Buildings\*: {r['buildings_scaled']}",
                    inline=False,
                )
            else:
                embed.add_field(
                    name=recipe, value="Recipe not found", inline=False
                )
        embed.add_field(name="Notes", value="*Buildings\* (Scaled) Scales the buildings by the sum of the number of items going in and out for a given recipe. This is based on the recipe, not the building type. (Factored to be 1 full Manufacturer = 3 Assemblers = 9 Constructors)*\n\n*Resources\* (Scaled) Scales the resources by the inverse of the quantity available on the map.*")
        await ctx.reply(embed=embed)

    @commands.command(name="tstats", description="get your stats")
    async def tstats(self, ctx, *, user=None):
        profile = get_user_profile(str(ctx.author.id))["characters"]["pmc"]
        embed = discord.Embed(
            title=f"{profile['Info']['Nickname']}, L{profile['Info']['Level']} {profile['Info']['Side']} {profile['SurvivorClass']}"
        )
        skills = calculate_skill_levels(profile["Skills"]["Common"])
        skills_text = f"""__Physical__\nEndurance: {skills["Endurance"]}   Strength: {skills["Strength"]}\n
                    Vitality: {skills["Vitality"]}   Health: {skills["Health"]}\n
                    Metabolism: {skills["Metabolism"]}   Stress Resist: {skills["StressResistance"]}\n
                    Immunity: {skills["Immunity"]}\n   Strength: {skills["Strength"]}\n
                    Endurance: {skills["Endurance"]}   Strength: {skills["Strength"]}\n
                    Endurance: {skills["Endurance"]}   Strength: {skills["Strength"]}\n
                    Endurance: {skills["Endurance"]}   Strength: {skills["Strength"]}\n
                    """
        embed.add_field(name="Skills", value=skills_text)

        await ctx.reply(embed=embed)
    @commands.command(name="twill", description="get wills tasks")
    async def twill(self, ctx):
        will = "67429c83000249e109c2a8fd"
        wills_quests = get_user_profile(will)["characters"]["pmc"]["Quests"]
        quests_info = load_json("strings/quests.json")
        location_mapping = load_json("strings/locations.json")
        quest_info_dict = extract_quest_info(quests_info, location_mapping)

        filtered_qids = filter_quests_with_status_2(wills_quests)

        quests_by_location = defaultdict(list)
        for qid in filtered_qids:
            quest_name = quest_info_dict.get(qid, {}).get("QuestName", qid)
            location = quest_info_dict.get(qid, {}).get("Location", "???")
            if quest_name == "Unknown Quest":
                quest_name = qid  # Use qid if the quest name is unknown
            quests_by_location[location].append(quest_name)

        # Sort the locations and quests
        sorted_locations = sorted(quests_by_location.items())
        for location in quests_by_location:
            quests_by_location[location].sort()

        # Create the embed
        embed = discord.Embed(
            title=f"Tarkov Quest Comparison\n{self.tarkov_users[will]['tarkov_nick']}",
            color=discord.Color.blue(),
        )

        # Add fields for each location
        for location, quest_names in sorted_locations:
            quest_list = "\n".join(quest_names)
            embed.add_field(
                name=f"__{location}__",
                value=quest_list if quest_list else "No quests",
                inline=False,
            )

        await ctx.reply(embed=embed)

    @commands.command(name="tcompare", description="compare quests")
    async def tcompare(self, ctx, *, user=None):
        # Load quest and location data

        if not user:
            user1 = "439606776187584523"
            user2 = "182968537646759937"

        # if not user1 or (user1 and user2 not in self.tarkov_users.keys()):
        #     await ctx.reply("You need to link a valid username or provide valid nicks.")
        #     return
        # else:
        #     user1 = user1.id
        #     user2 = user2.id
        user1_quests = get_user_profile(user1)["characters"]["pmc"]["Quests"]
        user2_quests = get_user_profile(user2)["characters"]["pmc"]["Quests"]
        # punch = load_json(f'.json')["characters"]["pmc"]["Quests"]
        # mcgnarman = load_json('/home/cody/fika/user/profiles/66bb114800046660b9d56048.json')["characters"]["pmc"]["Quests"]
        quests_info = load_json("strings/quests.json")
        location_mapping = load_json("strings/locations.json")

        # Extract quest information from the quests_info file with location mapping
        quest_info_dict = extract_quest_info(quests_info, location_mapping)

        # Filter quests with status: 2 from both JSON files
        filtered_qids_1 = filter_quests_with_status_2(user1_quests)
        filtered_qids_2 = filter_quests_with_status_2(user2_quests)

        # Find common qids between the two JSON files
        common_qids = filtered_qids_1.intersection(filtered_qids_2)

        # Group quests by location and sort them
        quests_by_location = defaultdict(list)
        for qid in common_qids:
            quest_name = quest_info_dict.get(qid, {}).get("QuestName", qid)
            location = quest_info_dict.get(qid, {}).get("Location", "???")
            if quest_name == "Unknown Quest":
                quest_name = qid  # Use qid if the quest name is unknown
            quests_by_location[location].append(quest_name)

        # Sort the locations and quests
        sorted_locations = sorted(quests_by_location.items())
        for location in quests_by_location:
            quests_by_location[location].sort()

        # Create the embed
        embed = discord.Embed(
            title=f"Tarkov Quest Comparison\n{self.tarkov_users[user1]['tarkov_nick']} = {self.tarkov_users[user2]['tarkov_nick']}",
            color=discord.Color.blue(),
        )

        # Add fields for each location
        for location, quest_names in sorted_locations:
            quest_list = "\n".join(quest_names)
            embed.add_field(
                name=f"__{location}__",
                value=quest_list if quest_list else "No quests",
                inline=False,
            )

        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(TarkovCog(bot))
