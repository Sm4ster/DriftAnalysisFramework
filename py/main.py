from fastapi import FastAPI, WebSocket
from DriftAnalysis import DriftAnalysis
from datetime import datetime
import time
import uuid

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()

        if data["message"] == "start_run":
            print("started_a new run")
            run_id = str(uuid.uuid4())
            await websocket.send_json({"message": "run_started", "data": {"uuid": run_id, "config": data['config'],
                                                                          "started_at": datetime.now().strftime(
                                                                              "%Y-%m-%d %H:%M:%S")}})
            await start_run(run_id, data['config'], websocket)


async def start_run(run_id, config, websocket: WebSocket):
    # create the DriftAnalysisClass
    analysis = DriftAnalysis(config, True)

    # send all locations to the frontend
    print(analysis.min_max)
    await websocket.send_json(
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
            await websocket.send_json(
                {"message": "partial_results", "data": {"run_id": run_id, "results": to_list(new_results)}})
        time.sleep(1)

    await websocket.send_json({"message": "run_finished",
                               "data": {"uuid": run_id, "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})
    print("finished_sending_data")


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
