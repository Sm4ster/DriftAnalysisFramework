import asyncio, threading
import time, uuid

from fastapi import FastAPI, WebSocket
from DriftAnalysis import DriftAnalysis
from datetime import datetime



app = FastAPI()

class WebSocketSafe:
    def __init__(self, websocket: WebSocket):
        self.lock = threading.Lock()
        self.connection = websocket

    async def receive(self):
        self.lock.acquire()
        try:
            data = await self.connection.receive_json()
        except:
            data = self.receive()
        finally:
            self.lock.release()
        return data

    async def send(self, data):
        self.lock.acquire()
        try:
            success = await self.connection.send_json(data)
        except:
            success = self.send(data)
        finally:
            self.lock.release()
        return success

@app.websocket("/ws")
async def websocket_endpoint(websocket_: WebSocket):
    await websocket_.accept()

    stop_threads = False
    open_jobs = []
    counter = 0

    # Initialize wrapper for thread safety
    websocket = WebSocketSafe(websocket_)
    while True:
        print(open_jobs)

        try:
            data = await websocket.receive()
        except:
            print("The user went offline and so will I.")
            break

        if data["message"] == "open_runs":
            # Load all open jobs for this user
            print("Checking all open jobs")

        if data["message"] == "ping":
            thread = threading.Thread(target=asyncio.run, args=(test(websocket, open_jobs, counter),))
            thread.start()
            counter += 1

        if data["message"] == "start_run":
            # make a run uuid
            run_id = str(uuid.uuid4())

            # send the run with uuid and the configuration as well as the server time back to the client
            await websocket.send({"message": "run_started", "data": {"uuid": run_id, "config": data['config'],
                                                                          "started_at": datetime.now().strftime(
                                                                              "%Y-%m-%d %H:%M:%S")}})
            thread = threading.Thread(target=asyncio.run, args=(start_run(run_id, data['config'], websocket),))
            print(thread)


async def start_run(run_id, config, websocket: WebSocketSafe):
    # create the DriftAnalysisClass
    analysis = DriftAnalysis(config, True)

    # send all locations to the frontend
    await websocket.send(
        {"message": "locations", "data":
            {
                "run_id": run_id,
                "locations": to_list(analysis.get_locations()),
                "min_max": analysis.min_max
            }
         })

    analysis.start()

    while not analysis.all_jobs_in_results():
        print("Hello from this loop")
        new_results = analysis.get_new_results()
        if len(new_results):
            await websocket.send(
                {"message": "partial_results", "data": {"run_id": run_id, "results": to_list(new_results)}})
        time.sleep(1)

    await websocket.send({"message": "run_finished",
                               "data": {"uuid": run_id, "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})
    print("finished_sending_data")

async def send_new_data(websocket: WebSocketSafe, stop, open_runs, open_jobs):
    print("do something")

async def test(websocket: WebSocketSafe, open_jobs, counter):
    print("I am going to sleep now")
    time.sleep(5)
    print("I HAVE RISEN UP FROM THE DEAD")
    await websocket.send({"message": "pong"})
    open_jobs.append("foo" + str(counter))

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