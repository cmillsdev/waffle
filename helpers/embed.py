from discord import Embed
# from hurry.filesize import size
from helpers.utils import percentage, size
from strings.link_msg import get_link_msg
from config import DEBRID_WEBDAV, DL_CHANNEL
from urllib.parse import quote

def fortnite(stats):
    print(f"Building embed for {stats.user.name}")
    embed = Embed(
        title=f"{stats.user.name}",
        description=f"**Battle Pass:** {stats.battle_pass.level}",
    )
    overall = stats.stats.all.overall
    solo = stats.stats.all.solo
    duo = stats.stats.all.duo
    squad = stats.stats.all.squad
    embed.add_field(
        name="__Overall__",
        value=f"**Matches(Win rate):** {overall.matches} (*{overall.win_rate}%*)\n**K/D(ratio):** {overall.kills}/{overall.deaths} (*{overall.kd}*)\n**Kills\\Match:** {overall.kills_per_match} | **Kills\\Min:** {overall.kills_per_min}\n**Minutes Played:** {overall.minutes_played} | **Players Outlived:** {overall.players_outlived}",
        inline=False,
    )
    try:
        embed.add_field(
            name="__Solo__",
            value=f"**Matches(Win rate):** {solo.matches} (*{solo.win_rate}%*)\n**K/D(ratio):** {solo.kills}/{solo.deaths} (*{solo.kd}*)\n**Kills\\Match:** {solo.kills_per_match} | **Kills\\Min:** {solo.kills_per_min}\n**Minutes Played:** {solo.minutes_played} | **Players Outlived:** {solo.players_outlived}",
            inline=False,
        )
    except:
        embed.add_field(
            name="__Solo__",
            value="No stats for this season.\nPlay some games.",
            inline=False,
        )
    try:
        embed.add_field(
            name="__Duo__",
            value=f"**Matches(Win rate):** {duo.matches} (*{duo.win_rate}%*)\n**K/D(ratio):** {duo.kills}/{duo.deaths} (*{duo.kd}*)\n**Kills\\Match:** {duo.kills_per_match} | **Kills\\Min:** {duo.kills_per_min}\n**Minutes Played:** {duo.minutes_played} | **Players Outlived:** {duo.players_outlived}",
            inline=False,
        )
    except:
        embed.add_field(
            name="__Duo__", value="No stats for this season.\nPlayyyyyy.", inline=False
        )
    try:
        embed.add_field(
            name="__Squad__",
            value=f"**Matches(Win rate):** {squad.matches} (*{squad.win_rate}%*)\n**K/D(ratio):** {squad.kills}/{squad.deaths} (*{squad.kd}*)\n**Kills\\Match:** {squad.kills_per_match} | **Kills\\Min:** {squad.kills_per_min}\n**Minutes Played:** {squad.minutes_played} | **Players Outlived:** {squad.players_outlived}",
            inline=False,
        )
    except:
        embed.add_field(
            name="__Squad__",
            value="No squad stats, seriously?\nWhere are you on Fridays?",
            inline=False,
        )
    print(f"Built embed for {stats.user.name}")
    return embed


def hltb(name, results):
    print(f"Building embed for {results[0].game_name}")
    embed = Embed(
        title=f"HLTB Results for {name}",
        url="https://howlongtobeat.com?q=" + name.replace(" ", "+"),
    )
    embed.set_thumbnail(url=results[0].game_image_url)
    if len(results) < 5:
        for x in results:
            platforms = ""
            for p in x.profile_platforms:
                platforms += f"{p}, "
            embed.add_field(
                name=f"{x.game_name} ({x.release_world})",
                value=f"**Dev:** {x.profile_dev}\n**Platforms:** {platforms[:-2]}\n**Main Story:** {x.main_story}h | **Main + Extras:** {x.main_extra}h\n**Completionist:** {x.completionist}h | **All:** {x.all_styles}h\n{x.game_web_link}",
                inline=False,
            )
    else:
        for i in range(4):
            platforms = ""
            for p in results[i].profile_platforms:
                platforms += f"{p}, "
            embed.add_field(
                name=f"{results[i].game_name} ({results[i].release_world}))",
                value=f"**Dev:** {results[i].profile_dev}\n**Platforms:** {platforms[:-2]}\n**Main Story:** {results[i].main_story}h | **Main + Extras:** {results[i].main_extra}h\n**Completionist:** {results[i].completionist}h | **All:** {results[i].all_styles}h\n{results[i].game_web_link}",
                inline=False,
            )
    print(f"Built embed for {results[0].game_name}")
    return embed


# debrid embeds
def debrid_status(all_status):
    embed = Embed(title="__Download Status__", color=0x00FF00)
    for m in all_status:
        try:
            name = all_status[m].get("filename", "")
            dlsize = float(all_status[m].get("size", 0))
            seeders = all_status[m].get("seeders", 0)
            speed = all_status[m].get("downloadSpeed", 0)
            complete = float(all_status[m].get("downloaded", 0))
        except TypeError:
            name = m.get("filename", "")
            dlsize = float(m.get("size", 0))
            seeders = m.get("seeders", 0)
            speed = m.get("downloadSpeed", 0)
            complete = float(m.get("downloaded", 0))

        sized_size = 0
        percentage_complete = "0%"
        if dlsize > 0:
            sized_size = size(int(dlsize))
        if speed > 0:
            speed = size(int(speed))
        if complete > 0:
            percentage_complete = percentage(complete, dlsize)
        embed.add_field(
            name=name,
            value=f"{percentage_complete} of {sized_size} | Seeders: {seeders} | Speed: {speed}",
            inline=False,
        )
    return embed

def download_ready_from_queue(author, magnet, link=None):
    embed = Embed(description=f"<@{author}>")
    if link is None:
        link = f"{DEBRID_WEBDAV}magnets/{quote(magnet)}/"
    embed.add_field(
        name=f"{magnet}",
        value=f"[{get_link_msg()}]({link})",
    )
    return embed

def download_ready(author, magnets, link=None):
    embed = Embed(description=f"<@{author}>")
    for magnet in magnets['ready']:
        if link is None:
            link = f"{DEBRID_WEBDAV}magnets/{quote(magnet)}/"
        embed.add_field(
            name=f"{magnet}",
            value=f"[{get_link_msg()}]({link})", inline=False
        )
    return embed

def status_embed(ready_list):
    embed = Embed()
    for magnet in ready_list['ready']:
        embed.add_field(name=magnet, value=f'Sent to <#{DL_CHANNEL}>', inline=False)
    for magnet in ready_list['not_ready']:
        print(magnet)
        embed.add_field(name=magnet['name'], value=f'Not ready, added to queue.',inline=False)
    return embed

def torrent_results(results):
    embed = Embed()
    x = 0
    for torrent in results:
        result_value = f"Seeders: {torrent['seeders']} | Leechers: {torrent['leechers']} | Size: {torrent['size_in_bytes']}"
        embed.add_field(
            name=f"{x+1}. {torrent['name']}",
            value=result_value,
            inline=False,
        )
        x = x + 1
    embed.add_field(
        name="----------------",
        value="You should pick the one with the most seeders and a reasonable filesize. Pay attention to the quality. You dont want a cam or TS.\n*!pick 1-10, !pick 1,3,5, !pick 1.\nSupports range or comma-separated picks.*",
        inline=False,
    )
    print("Built embed for torrent results")
    return embed