import discord
from discord.ext import commands
from discord.ext import tasks
from cogwatch import watch
from config import (
    TWITCH_CHANNEL,
    TWITCH_NOTIFY_ROLE,
    TWITCH_CLIENT_ID,
    TWITCH_SECRET,
    DL_CHANNEL,
    DEBRID_WEBDAV,
)
from loguru import logger
from utils.connection import Connection as Conn
import urllib.parse
from utils.urls import Urls
from utils.random import get_link_msg
from utils.embed import download_ready, stream_embed
from utils.db import DB

MY_GUILD = discord.Object(id=771867774087725146)


class Waffle(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!", description="waffle", intents=discord.Intents.all()
        )
        # self.tree = discord.app_commands.CommandTree(self)
        logger.add("logs/waffle.log", rotation="7 MB", retention="10 days")
        logger.level("DEBUG")
        logger.info("Logging is set up!")

        self.twitch_headers = ""
        self.db = DB()

    async def setup_hook(self):
        self.debrid_check.start()
        self.twitch_check.start()
        logger.info("Background tasks started.")

    @watch(path="cogs", preload=True)
    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="8=====D~~"))

        logger.info(
            f"\n\nLogged in as: {self.user.name} - {self.user.id}\nVersion: {discord.__version__}\n"
        )
        logger.info("Successfully logged in and booted...!")
        logger.info("Cogwatch is running!")

    async def on_message(self, message):
        if message.author.bot:
            return

        await self.process_commands(message)

    async def get_twitch_headers(self):
        try:
            body = {
                "client_id": TWITCH_CLIENT_ID,
                "client_secret": TWITCH_SECRET,
                "grant_type": "client_credentials",
            }
            async with Conn() as resp:
                keys = await resp.post_json(Urls.TWITCH_TOKEN_REQUEST, data=body)
            logger.info("Twitch token refreshed")
            self.twitch_headers = {
                "Client-ID": TWITCH_CLIENT_ID,
                "Authorization": "Bearer " + keys["access_token"],
            }
        except Exception as e:
            logger.exception(e)

    @tasks.loop(seconds=15)
    async def twitch_check(self):
        twitch_channel = await self.fetch_channel(TWITCH_CHANNEL)
        twitchers = await self.db.get_twitchers()
        twitchers = list(twitchers)
        # logger.debug("Checking twitchers...")
        try:
            for t in twitchers:
                async with Conn() as resp:
                    stream_data = await resp.get_json(
                        Urls.TWITCH_URL + t["user"], headers=self.twitch_headers
                    )
                try:
                    logger.debug(stream_data)
                    logger.debug(t)
                    if stream_data != [] and stream_data["data"][0]["type"] == "live":
                        if not t["online"]:
                            embed = stream_embed(
                                t["user"],
                                stream_data["data"][0]["title"],
                                stream_data["data"][0]["game_name"],
                            )
                            await self.db.set_twitcher_status(t["user"], True)
                            logger.info(f"{t['user']} is online.")
                            await twitch_channel.send(embed=embed)
                    elif stream_data == []:
                        if t["online"]:
                            await self.db.set_twitcher_status(t["user"], False)
                            logger.info(f"{t['user']} is offline.")
                except (TypeError, KeyError, IndexError) as e:
                    logger.exception(e)
        except KeyError as e:
            logger.exception(e)
            await self.get_twitch_headers()

    @twitch_check.before_loop
    async def before_twitch_check(self):
        await self.wait_until_ready()
        await self.get_twitch_headers()

    @tasks.loop(seconds=20)
    async def debrid_check(self):
        # await self.twitch_check()

        queue = await self.db.get_active_queue()
        queue = list(queue)
        if len(queue) > 0:
            # logger.info(f"{queue}")
            for id in queue:
                if "active" in id["status"]:
                    logger.info(f"Checking: {id['task_id']}")
                    if "link" in id["type"]:
                        async with Conn() as resp:
                            r = await resp.get_json(
                                Urls.DEBRID_DELAYED + str(id["task_id"])
                            )
                            logger.info(Urls.DEBRID_DELAYED + str(id["task_id"]))
                            logger.debug(r)

                        if r["data"]["status"] == 2:
                            link = r["data"]["link"]
                            link_split = link.split("/")[-2:]
                            filename = urllib.parse.unquote(link_split[1])
                            logger.info(f"removing {id['task_id']}")
                            await self.db.set_status(id["task_id"], "complete")
                            embed = download_ready(id["user_id"], filename, link)
                            dl_channel = await self.fetch_channel(DL_CHANNEL)
                            await dl_channel.send(embed=embed)
                    else:
                        try:
                            async with Conn() as resp:
                                status_json = await resp.get_json(
                                    Urls.DEBRID_STATUS_ONE + str(id["task_id"])
                                )
                        except Exception as e:
                            logger.exception(e)
                            pass
                        try:
                            if (
                                status_json["status"] == "error"
                                or status_json["data"]["magnets"]["statusCode"] > 4
                            ):
                                await self.db.set_status(id["task_id"], "failed")
                                logger.info(f"removing {id['task_id']}")

                            elif "Ready" in status_json["data"]["magnets"]["status"]:
                                await self.db.set_status(
                                    task_id=id["task_id"], status="complete"
                                )
                                filename = status_json["data"]["magnets"]["filename"]
                                embed = download_ready(id["user_id"], filename)
                                logger.info(f"Removed: {id['task_id']}")
                                dl_channel = await self.fetch_channel(DL_CHANNEL)
                                await dl_channel.send(embed=embed)
                        except Exception as e:
                            logger.exception(e)
                            pass

    @debrid_check.before_loop
    async def before_task(self):
        await self.wait_until_ready()
