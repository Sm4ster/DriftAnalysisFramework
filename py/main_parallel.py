import json
import subprocess
import sys
from pathlib import Path

# Path to your JSON file
JSON_FILE = "machines.json"

# Name of the main tmux session
TMUX_SESSION = "remote_workers"

# Command to run remotely – change this to your actual task
REMOTE_COMMAND_TEMPLATE = "echo 'This should be the actual command for the run'"

def load_machine_list(json_path):
    with open(json_path, "r") as f:
        return json.load(f)

def add_tmux_window(session_name, window_name, ssh_command):
    subprocess.run([
        "tmux", "new-window",  "-t", session_name, "-n", window_name,
        ssh_command
    ], check=True)

def main():
    json_path = Path(JSON_FILE)
    if not json_path.exists():
        print(f"JSON file not found: {json_path}")
        sys.exit(1)

    machine_list = load_machine_list(json_path)

    # create tmux session
    session_name = f"remote_workers"
    subprocess.run(["tmux", "new-session", "-d", "-s", session_name], check=True)

    for idx, entry in enumerate(machine_list):
        hostname = entry["hostname"]
        workers = entry["workers"]


        remote_cmd = REMOTE_COMMAND_TEMPLATE.format(workers=workers)
        ssh_cmd = f"ssh {hostname} 'echo $(hostname); {remote_cmd}; exec $SHELL -l; '"

        print(f"Creating tmux session '{session_name}' to run on {hostname}...")

        # add commands in new windows
        add_tmux_window(session_name, hostname, ssh_cmd)

    # remove the first window of the session, as it is not used
    subprocess.run(["tmux", "kill-window", "-t", f"{session_name}:1"], check=True)
    subprocess.run(["tmux", "move-window", "-r", "-t", session_name], check=True)

    print("✅ All tmux sessions started.")

if __name__ == "__main__":
    main()