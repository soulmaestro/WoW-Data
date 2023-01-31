import queue, time, urllib.request
from threading import Thread

from blizzardapi import BlizzardApi
from dotenv import load_dotenv
import json
import datetime
import os



load_dotenv()

#Define your API credentials
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
region = os.getenv("REGION")
locale = os.getenv("LOCALE")


api_client = BlizzardApi(client_id, client_secret)



def perform_web_requests(ids, no_workers):
    class Worker(Thread):
        def __init__(self, request_queue):
            Thread.__init__(self)
            self.queue = request_queue
            self.results = []

        def run(self):
            while True:
                time.sleep(0.02)
                id = self.queue.get()
                if id == "":
                    break
                # request = urllib.request.Request(content)

                try:
                    # response = api_client.wow.game_data.get_spell(region, locale,id)
                    response = api_client.wow.game_data.get_recipe(region, locale,id)
                except:
                    print(f"BIG ERROR with {id}")
                    self.results.append(id)
                    time.sleep(1)
                else:
                    try:
                        code = response["_links"]
                    except:
                        print(f"no such item with id: {id}")
                    else:
                        file=str(id)+".json"
                        local_filename = os.path.join(r"data2","spell", file)
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
    for id in ids:
        q.put(id)

    # Workers keep working till they receive an empty string
    for _ in range(no_workers):
        q.put("")

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
ids = [
358605,
358643
    ]
results = perform_web_requests(ids, 2)
print(f"failed to get data for : ")

for result in results:
    print(f"{result},")