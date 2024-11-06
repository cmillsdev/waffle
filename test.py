import requests
import json
# ignore partycontroltimeseriesdata (for now?)
# resultsmeta, partycontroldata

# https://static01.nyt.com/elections-assets/pages/data/2024-11-05/results-arizona-president.json - state pages
URL = "https://static01.nyt.com/elections-assets/pages/data/2024-11-05/results-president.json"

results = requests.get(URL).json()

races = results['races']
for race in races:
    state_name = race['top_reporting_unit']['name']
    trump_votes = race['top_reporting_unit']['candidates'][0]['votes']['total']
    harris_votes = race['top_reporting_unit']['candidates'][1]['votes']['total']

    if trump_votes != 0 and harris_votes != 0:
        print(f"{state_name}: T: {trump_votes} | H: {harris_votes}")
