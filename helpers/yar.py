import httpx
import xmltodict
from config import JACKETT_KEY

def filter_result(item, keys_to_remove):
    if item.get('seeders') == 16777215:
        return None
    return {key: value for key, value in item.items() if key not in keys_to_remove}

def search_magnets(q):
    url = f"http://wafflefm:4000/api/search/{q}"

    with httpx.Client() as client:
        response = client.get(url, timeout=60)

    api_results = response.json()['data']

    # keys_to_remove = {'canonical_url', 'category', 'description', 'id', 'magnet_hash', 'published_at'}

    # Filter and transform each result, removing any with 'seeders' == 16777215
    # filtered_results = [
    #     filtered_item for item in api_results 
    #     if (filtered_item := filter_result(item, keys_to_remove)) is not None
    # ]

    # Sort the filtered results by 'seeders' in descending order
    sorted_results = sorted(filtered_results, key=lambda item: item['seeders'], reverse=True)

    return sorted_results[:10] # limited to ten results

def jackett_search(query):
    # internetarchive - separate
    # nyaasi - separate
    indexers = ['bitsearch', 'nyaasi']
    query = query.replace(' ', '+')
    # replace(' ', '+')
    # rss.channel.item
    # get results from both, combine, filter down to handful of keys, sort by seeders, slice down to 10
    filtered_results = []
    try:
        for i in indexers:
            url = f"http://dietpi:9117/api/v2.0/indexers/{i}/results/torznab/api?apikey={JACKETT_KEY}&t=search&q={query}"
            with httpx.Client() as client:
                response = client.get(url, timeout=60)
            torrent_results = xmltodict.parse(response.text) #['rss']['channel']['item']
            if not torrent_results.get('error'):
                for torrent in torrent_results['rss']['channel']['item']:
                    for value in torrent["torznab:attr"]:
                        if value["@name"] == "seeders":
                            seeders = value["@value"]
                        if value["@name"] == "peers":
                            peers = value["@value"]
                    item = {"name": torrent['title'], "magnet_url": torrent['guid'], "size_in_bytes": torrent["size"], "source": torrent["jackettindexer"]["#text"], "seeders": int(seeders), "leechers": peers}
                    filtered_results.append(item)

        sorted_results = sorted(filtered_results, key=lambda item: item['seeders'], reverse=True)
        return sorted_results[:10]
    except Exception as e:
        print(e)
        results = {}
        results["error"] = "No results"
        return results


def eval_pick(pick):
    # pick will be one number, a range of numbers('1-5'), or a list of numbers('1,2,3,4,5')
    # need to return a list of numbers
    pick = pick.lower().replace('!pick', '').strip()
    pick_list = []
    if pick.isdigit():
        pick_list.append(int(pick.strip()) - 1)
    elif "-" in pick:
        start, end = pick.split("-")
        pick_list.extend(range(int(start.strip()) - 1, int(end.strip())))
    elif "," in pick:
        pick_list.extend([int(x) - 1 for x in pick.replace(" ", "").split(",")])
    for pick in pick_list:
        if pick < 0 or pick > 10:
            return False
    return pick_list

def build_magnet_list(picks, results):
    magnets = []
    for pick in picks:
        magnets.append(results[pick]['magnet_url'])

    return magnets

def build_ready_list(magnet_responses):
    ready_list = {"ready":[], "not_ready": []}
    for magnet in magnet_responses:
        if magnet['ready']:
            ready_list['ready'].append(magnet['name'])
        else:
            ready_list['not_ready'].append(magnet['name'])
    return ready_list