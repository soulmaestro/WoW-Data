
import queue, time, urllib.request
from threading import Thread

from blizzardapi import BlizzardApi
from dotenv import load_dotenv
import json
import datetime
import os
import pickle



load_dotenv()

#Define your API credentials
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
region = os.getenv("REGION")
locale = os.getenv("LOCALE")


api_client = BlizzardApi(client_id, client_secret)

results = []

def get_professions():
    response = ""

    try:
        response = api_client.wow.game_data.get_professions_index(region, locale)
    except:
        print(f"Failed to get all professions")
    else:
        # print(response)
        map = os.path.join(r"data3","profession")
        if not os.path.isdir(map):
            os.makedirs(map)

        file="_index.json"
        local_filename = os.path.join(map, file)
        lf = open(local_filename, "w")
        json.dump(response, lf, indent=4)
        lf.close()

        # print(f"data about item with ID {id} saved to file")

        for profession in response["professions"]:
            id = profession["id"]

            # file = str(id) + ".json"
            # local_filename = os.path.join(map, file)
            # lf = open(local_filename, "w")
            # json.dump(response, lf, indent=4)
            # lf.close()

            name = profession["name"]
            fname = f"{id} ({name})"
            map2 = os.path.join(map,fname)

            if not os.path.isdir(map2):
                os.makedirs(map2)
            get_skilltier(id,map2)


def get_skilltier(prof_id,map3):
    response3 =""

    try:
        response3 = api_client.wow.game_data.get_profession(region, locale,prof_id)
    except:
        print(f"Failed to get skill-tiers for profession {name}")
    else:
        # print(response)
        # map = os.path.join(r"data2","profession",name)
        # if not os.path.isdir(map):
        #     os.makedirs(map)

        file = "_index.json"
        local_filename = os.path.join(map3, file)
        lf = open(local_filename, "w")
        json.dump(response3, lf, indent=4)
        lf.close()

        # print(f"data about item with ID {id} saved to file")
        try:
            tier = response3["skill_tiers"]
        except:
            print(f"No skill tiers for profession {prof_id}")
        else:

            for skill_tier in response3["skill_tiers"]:
                tier_id = skill_tier["id"]

                # file = str(id) + ".json"
                # local_filename = os.path.join(map, file)
                # lf = open(local_filename, "w")
                # json.dump(response, lf, indent=4)
                # lf.close()

                name = skill_tier["name"].replace("/","-")
                fname = f"{tier_id} ({name})"
                map4 = os.path.join(map3,fname)

                if not os.path.isdir(map4):
                    os.makedirs(map4)
                get_tierrecipies(prof_id, tier_id, map4)



def get_tierrecipies(prof_id, tier_id, map5):
    response4 = ""

    try:
        response4 = api_client.wow.game_data.get_profession_skill_tier(region, locale, prof_id, tier_id)
    except:
        print(f"can't get recipies for prof:{prof_id} and skill_tier: {tier_id}")
    else:
        file = "_index.json"
        local_filename = os.path.join(map5, file)
        lf = open(local_filename, "w")
        json.dump(response4, lf, indent=4)
        lf.close()

        try:
            tier = response4["categories"]
        except:
            print(f" no categories for {prof_id} and {tier_id}")
        else:
            for category in response4["categories"]:
                cat_name = category["name"]
                map6 = os.path.join(map5,cat_name)
        
                if not os.path.isdir(map6):
                    os.makedirs(map6)

                try:
                    recs = category["recipes"]
                except:
                    print(f"no recipies for {prof_id} and {tier_id} and {cat_name}")
                else:
                    for recipe in category["recipes"]:
                        new_recipe = {"id":recipe["id"],"map": map6}
                        recipes.append(new_recipe)
                        # get_recipe(recipe[id],map6)


# def get_recipe(recipe_id,map7):
#     response5 = ""
#     try:
#         response5 = api_client.wow.game_data.get_recipe(region, locale,recipe_id)
#     except:
#         print(f"can't get data for recipe: {recipe_id}")
#     else:
#         file = recipe_id+".json"
#         local_filename = os.path.join(map7, file)
#         lf = open(local_filename, "w")
#         json.dump(response5, lf, indent=4)
#         lf.close()




def get_recipes(recipes, no_workers):
    class Worker(Thread):
        def __init__(self, request_queue):
            Thread.__init__(self)
            self.queue = request_queue
            self.results = []

        def run(self):
            while True:
                info = pickle.loads(self.queue.get())
                id = info["id"]
                if info == "":
                    break
                # request = urllib.request.Request(content)
                if id == "":
                    break
                try:
                    time.sleep(0.02)
                    response = api_client.wow.game_data.get_recipe(region, locale,id)
                except:
                    print(f"BIG ERROR with {id}")
                    self.results.append(pickle.dumps(info))
                    time.sleep(1)
                else:
                    try:
                        code = response["_links"]
                    except:
                        print(f"no such recipe with id: {id}")
                    else:
                        file=str(id)+".json"
                        local_filename = os.path.join(info["map"], file)
                        lf = open(local_filename, "w")

                        json.dump(response, lf, indent=4)

                        # test = lf.write(str(response))
                        lf.close()
                        print(f"data about item with ID {id} saved to file")
                    finally:
                        # self.results.append(id)
                        self.queue.task_done()                

                # self.results.append(response)
                # self.queue.task_done()

    # Create queue and add addresses
    q = queue.Queue()
    for recipe in recipes:
        q.put(pickle.dumps(recipe))

    # Workers keep working till they receive an empty string
    for _ in range(no_workers):
        q.put(pickle.dumps({"id":"","map":""}))

    # Create workers and add tot the queue
    workers = []
    for _ in range(no_workers):
        worker = Worker(q)
        worker.start()
        workers.append(worker)
    # Join workers to wait till they finished
    for worker in workers:
        worker.join()

    # Combine results from all workers
    r = []
    for worker in workers:
        r.extend(worker.results)
    return r
    
# low_id = 1
# max_id = 50000
# results = perform_web_requests(low_id, max_id, 2)

recipes=[]

profs = get_professions()

results =  get_recipes(recipes, 2)


print(f"failed to get data for : ")


for result in results:
    print(f"{pickle.loads(result)},")