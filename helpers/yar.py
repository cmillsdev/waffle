import httpx

def search_magnets(q):
    url = f"http://192.168.1.238:4000/api/search/{q}"

    with httpx.Client() as client:
        response = client.get(url, timeout=60)

    api_results = response.json()['data']

    # Keys to remove from each result
    keys_to_remove = {'canonical_url', 'category', 'description', 'id', 'magnet_hash', 'published_at'}

    # Filter out unwanted keys for each item in the list
    filtered_results = [
        {key: value for key, value in item.items() if key not in keys_to_remove}
        for item in api_results
    ]

    # Sort the filtered results by 'seeders' in descending order
    sorted_results = sorted(filtered_results, key=lambda item: item['seeders'], reverse=True)

    return sorted_results


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
        magnets.append(magnets[pick]['magnet_url'])

    return magnets

def build_ready_list(magnet_responses):
    ready_list = {"ready":[], "not_ready": []}
    for magnet in magnet_responses:
        if magnet['ready']:
            ready_list['ready'].append(magnet['name'])
        else:
            ready_list['not_ready'].append(magnet['name'])
    return ready_list