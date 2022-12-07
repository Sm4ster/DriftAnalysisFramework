import asyncio, threading
import time, uuid

from fastapi import FastAPI, WebSocket
from DriftAnalysis import DriftAnalysis
from datetime import datetime

app = FastAPI()

# This just makes this variable call by reference
class StopThreads:
    value = False

class OpenRunsSafe:
    container = {}

    def __init__(self, ):
        self.lock = threading.Lock()

    def get(self, uuid):
        self.lock.acquire()
        try:
            data = self.container[uuid]
        finally:
            self.lock.release()
        return data

    def add(self, uuid, run):
        self.lock.acquire()
        try:
            self.container[uuid] = run
        finally:
            self.lock.release()

    def delete(self, uuid):
        self.lock.acquire()
        try:
            del self.container[uuid]
        finally:
            self.lock.release()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    stop_threads = StopThreads()
    open_runs = OpenRunsSafe()

    # Initialize wrapper for thread safety
    while True:
        try:
            data = await websocket.receive_json()
        except:
            stop_threads.value = True
            print("The user went offline and so will I.")
            break

        if data["message"] == "open_runs":
            # Load all open jobs for this user
            for run_uuid in data["data"]:
                # TODO load open jobs from the database, unfreeze them and store them in open_runs
                print(run_uuid)

            # start a background thread that sends new data to the user
            asyncio.create_task(send_new_data(websocket, open_runs, stop_threads))


        if data["message"] == "ping":
            print(open_runs.container)
            await websocket.send_json({"message": "pong"})
            # thread = threading.Thread(target=asyncio.run, args=(test(websocket),))
            # thread.start()

        if data["message"] == "start_run":
            # make a run uuid
            run_id = str(uuid.uuid4())

            # send the run with uuid and the configuration as well as the server time back to the client
            await websocket.send_json({"message": "run_started", "data": {"uuid": run_id, "config": data['config'],
                                                                     "started_at": datetime.now().strftime(
                                                                         "%Y-%m-%d %H:%M:%S")}})
            asyncio.create_task(start_run(run_id, data['config'], open_runs, websocket))
            #thread = threading.Thread(target=asyncio.run, args=(start_run(run_id, data['config'], open_runs, websocket),))
            #thread.start()

        if data["message"] == "run_finished_confirmed":
            print("removing run", data)
            open_runs.delete(data["data"]["uuid"])


async def start_run(run_id, config, open_runs: OpenRunsSafe, websocket: WebSocket):
    # create the DriftAnalysisClass
    analysis = DriftAnalysis(config, run_id, True)

    # send all locations to the frontend
    await websocket.send_json(
        {"message": "locations", "data":
            {
                "run_id": run_id,
                "locations": to_list(analysis.get_locations()),
                "min_max": analysis.min_max
            }
         })

    analysis.start()

    # add it to the open runs to keep the frontend informed
    open_runs.add(run_id, analysis)


async def send_new_data(websocket: WebSocket, open_runs: OpenRunsSafe, stop):
    while not stop.value:
        await asyncio.sleep(1)

        print(stop.value)

        print("doing stuff")
        for run in open_runs.container.items():
            # check for new results
            new_results = run[1].get_new_results()
            print("doing stuff")
            try:
                await websocket.send_json({"message": "pong"})
            except:
                print("something bad happened")

            # send if there is something new
            if len(new_results):
                print("sending results")
                await websocket.send_json(
                    {"message": "partial_results", "data": {"run_id": run[0], "results": to_list(new_results)}})

            # if the run is finished let the front end know
            if run[1].all_jobs_in_results():
                print("This is gonna end")
                await websocket.send_json({"message": "run_finished",
                                      "data": {"uuid": run[0],
                                               "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})


async def test(websocket: WebSocket):
    await websocket.send({"message": "pong"})


def to_list(data):
    if type(data) is dict:
        for key, value in data.items():
            data[key] = to_list(value)
        return data
    if type(data) is list:
        for key in range(len(data)):
            data[key] = to_list(data[key])
        return data
    if type(data).__module__ == "numpy":
        return data.tolist()
    return data


async def send_data(websocket: WebSocket, data):
    await websocket.send_json({"message": "pong"})
