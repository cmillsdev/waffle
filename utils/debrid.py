# https://docs.alldebrid.com
from bot import Waffle
from utils.connection import Connection as Conn
from utils.urls import Urls
from loguru import logger
import os


async def upload_magnet(magnet):
    try:
        async with Conn() as resp:
            r = await resp.get_json(Urls.DEBRID_UPLOAD + magnet)
        magnet_info = [
            r["data"]["magnets"][0]["id"],
            r["data"]["magnets"][0]["name"],
            r["data"]["magnets"][0]["ready"],
        ]
        return magnet_info
    except KeyError:
        print(r)
        return r["error"]["message"]


async def get_active_magnets():
    async with Conn() as resp:
        r = await resp.get_json(Urls.DEBRID_STATUS_ACTIVE)
    return r["data"]["magnets"]


async def get_all_magnet_status():
    async with Conn() as resp:
        r = await resp.get_json(Urls.DEBRID_STATUS)
    if len(r["data"]["magnets"]) <= 0:
        return 0
    else:
        return r["data"]["magnets"]


async def get_magnet_status(magnetid):
    try:
        async with Conn() as resp:
            r = await resp.get_json(Urls.DEBRID_STATUS_ONE + magnetid)
        return r["data"]["magnets"]["status"]
    except KeyError:
        return r["error"]["message"]


async def delete_magnet(magnetid):
    try:
        async with Conn() as resp:
            r = await resp.get_json(Urls.DEBRID_DELETE + magnetid)
        return r["data"]["message"]
    except KeyError:
        return r["error"]["message"]


def restart_magnet(magnetid):
    pass


async def instant_magnet(magnet):
    async with Conn() as resp:
        r = await resp.get_json(Urls.DEBRID_DELETE + magnet)
    return r["data"]["magnets"][0]["instant"]


def eval_pick(pick):
    # pick will be one number, a range of numbers('1-5'), or a list of numbers('1,2,3,4,5')
    # need to return a list of numbers
    pick_list = []
    if pick.isdigit():
        pick_list.append(int(pick.strip()) - 1)
    elif "-" in pick:
        start, end = pick.split("-")
        pick_list.extend(range(int(start.strip()) - 1, int(end.strip())))
    elif "," in pick:
        pick_list.extend([int(x) - 1 for x in pick.replace(" ", "").split(",")])
    logger.info(pick_list)
    return pick_list


async def get_tiktok_link(url):
    try:
        async with Conn() as resp:
            r = await resp.get_json(Urls.DEBRID_UNLOCK + url)
        file_id = r["data"]["id"]
        streams = r["data"]["streams"]
        for s in streams:
            if "h264" in s["format"]:
                stream_id = s["id"]
                stream_fs = s["filesize"]
                break

        async with Conn() as resp:
            r = await resp.get_json(
                f"{Urls.DEBRID_STREAMING}{file_id}&stream={stream_id}"
            )

        if stream_fs >= 8388000:
            logger.info("File too large")
            return "File too large"
        return r["data"]["link"]
        # download_tiktok_video(r["data"]["link"])

    except Exception as e:
        logger.exception(e)


async def download_tiktok_video(url):
    async with Conn() as resp:
        r = await resp.get(url)
        if r.status == 200:
            with open("tiktok.mp4", "wb") as f:
                async for data in r.content.iter_chunked(1024):
                    f.write(data)
    return "Downloaded"
