import asyncio, uuid, pickle
from redis import Redis

from fastapi import FastAPI, WebSocket
from DriftAnalysisFramework.DriftAnalysis import DriftAnalysis
from datetime import datetime

app = FastAPI()
open_runs = {}

r = Redis(host='nash.ini.rub.de', port=6379, db=0, password='4xEhjbGNkNPr8UkBQbWL9qmPpXpAeCKMF2G2')


# This just makes this variable call by reference
class StopThreads:
    value = False


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    stop_threads = StopThreads()

    # Initialize wrapper for thread safety
    while True:
        try:
            data = await websocket.receive_json()
        except:
            stop_threads.value = True
            # freeze all objects to the database
            for run in open_runs.items():
                # remove the queue, because it hinders the pickling
                run[1].q = None
                # print(run[1].jobs)
                r.set(run[0], pickle.dumps(run[1]))
                # print("I pickled successfully")

            # print("The user went offline and so will I.")
            break

        if data["message"] == "open_runs":
            # Load all open jobs for this user
            for run_uuid in data["data"]:
                run_object = r.get(run_uuid)
                if run_object:
                    print("Requested Object found, start sending data... (" + run_uuid + ")")
                    open_runs[run_uuid] = pickle.loads(run_object)
                    # print(open_runs[run_uuid].jobs)

                    # give the redis connection to give the queue back
                    open_runs[run_uuid].init_queue(r)

                else:
                    print("Requested object not found (" + run_uuid + ")")

            # start a background thread that sends new data to the user
            #asyncio.create_task(send_new_data(websocket, open_runs, stop_threads))

        if data["message"] == "ping":
            # print(open_runs["a0515314-e063-44e9-b1bc-c90baf702b1c"].jobs)
            await websocket.send_json({"message": "pong"})

        if data["message"] == "start_run":
            # make a run uuid
            run_id = str(uuid.uuid4())

            # send the run with uuid and the configuration as well as the server time back to the client
            await websocket.send_json({"message": "run_started", "data": {"uuid": run_id, "config": data['config'],
                                                                          "started_at": datetime.now().strftime(
                                                                              "%Y-%m-%d %H:%M:%S")}})

            asyncio.create_task(start_run(run_id, data['config'], open_runs, websocket))

        if data["message"] == "run_finished":
            # print("removing run", data)
            del open_runs[data["data"]["uuid"]]

        if data["message"] == "results_received":
            open_runs[data["data"]["run_id"]].remove_results(data["data"]["location_ids"])
            # print("removing results", data)


async def start_run(run_id, config, open_runs, websocket: WebSocket):

    # create the DriftAnalysisClass
    analysis = DriftAnalysis(config, run_id, redis_connection=r)

    # add it to the open runs to keep the frontend informed
    open_runs[run_id] = analysis

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


async def send_new_data(websocket: WebSocket, open_runs, stop):
    while not stop.value:
        await asyncio.sleep(5)

        # print("checking if there is data to send")
        for run in open_runs.items():
            # check for new results
            new_results = run[1].get_new_results()

            # send if there is something new
            if len(new_results):
                await websocket.send_json(
                    {"message": "partial_results", "data": {"run_id": run[0], "results": to_list(new_results)}})

            # if the run is finished let the front end know
            if run[1].all_jobs_in_results():
                # print("This is gonna end")
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
