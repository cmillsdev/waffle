from helpers import yar
from alldebrid import AllDebrid
from config import DEBRID_KEY

debrid = AllDebrid(apikey=DEBRID_KEY)


results = yar.search_magnets('fitgirl')
picks = yar.eval_pick('1-3')
magnet_list = yar.build_magnet_list(picks, results)

print(magnet_list)

resp = debrid.upload_magnets(magnet_list[0])

print(resp['data']['magnets'][0])