from fastapi import FastAPI, WebSocket
from DriftAnalysis import DriftAnalysis
import time
import uuid

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        print(data)
        print("\n")

        if data["message"] == "start_run":
            print("started_a new run")
            run_id = str(uuid.uuid4())
            await websocket.send_json({"message": "run_started", "data": {"uuid": run_id, "config": data['config']}})
            await start_run(run_id, data['config'], websocket)


async def start_run(run_id, config, websocket: WebSocket):
    # create the DriftAnalysisClass
    analysis = DriftAnalysis(config, False)

    # send all locations to the frontend
    await websocket.send_json(
        {"message": "locations", "data": {"run_id": run_id, "locations": to_list(analysis.get_starting_locations())}})

    analysis.start()

    while not analysis.all_jobs_in_results():
        print("Hello from this loop")
        new_results = analysis.get_new_results()
        if len(new_results):
            await websocket.send_json(
                {"message": "partial_results", "data": {"run_id": run_id, "results": to_list(new_results)}})
        time.sleep(1)

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
