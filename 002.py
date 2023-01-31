from blizzardapi import BlizzardApi
from dotenv import load_dotenv
import json
import datetime
import os

import queue, time, urllib.request
from threading import Thread


load_dotenv()

#Define your API credentials
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
region = os.getenv("REGION")
locale = os.getenv("LOCALE")


content = 1190456

api_client = BlizzardApi(client_id, client_secret)

# response = api_client.wow.game_data.get_modified_crafting_category_index(region = region, locale = locale)
try:
    # response = api_client.wow.game_data.get_item(region, locale,id)
    # response = api_client.wow.game_data.get_spell(region, locale,id)
    # response = api_client.wow.game_data.get_recipe(region, locale,id)
    response = api_client.wow.game_data.get_modified_crafting_category_index(region = region, locale = locale)
    
except:
    print(f"BIG ERROR with INDEX")
    # self.results.append(id)
    time.sleep(1)
else:
    try:
        code = response["_links"]
    except:
        print(f"no such item with index")
    else:
        file="_index.json"
        local_filename = os.path.join(r"data2","modified-crafting","category", file)
        lf = open(local_filename, "w")

        json.dump(response, lf, indent=4)


        # test = lf.write(str(response))
        lf.close()
        print(f"data about item with index saved to file")


print(response)