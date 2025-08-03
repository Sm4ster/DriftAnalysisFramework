import numpy as np
import argparse
import json
import os
from pathlib import Path

parser = argparse.ArgumentParser(description='This script computes stable kappa values for CMA.')
parser.add_argument('input_dir', type=str, help='Input directory name')
parser.add_argument('filename', type=str, help='File hash name')
args = parser.parse_args()

directory_path = f'./{args.input_dir}/parts/'


# data = []
# for filename in os.listdir(directory_path):
#     filepath = os.path.join(directory_path, filename)
#     with open(filepath, 'r', encoding='utf-8') as f:
#         data.append(json.load(f))
#


def combine_nan_arrays(arrays):
    if not arrays:
        raise ValueError("No arrays provided.")

    result = np.copy(arrays[0])
    for arr in arrays[1:]:
        result = np.where(np.isnan(result), arr, result)
    return result


# Initialisierung
keys = ['drift', 'standard_deviation', 'potential_after', 'precision']
combined = {key: [] for key in keys}
combined_info = {}
meta = None

final_data = {}

# Dateien laden
directory = Path(directory_path)
files = sorted(f for f in directory.iterdir() if f.name.startswith(args.filename))
for i, file in enumerate(files):
    filepath = str(file)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)

    if i == 0: final_data = content
    for key in keys:
        array = np.array(content[key])
        combined[key].append(array)
    for key, value in content["info"].items():
        array = np.array(value)
        if i == 0: combined_info[key] = []
        combined_info[key].append(array)

# Arrays kombinieren
for key in keys:
    combined_array = combine_nan_arrays(combined[key])
    final_data[key] = combined_array.tolist()

for key in final_data["info"].keys():
    combined_array = combine_nan_arrays(combined_info[key])
    final_data["info"][key] = combined_array.tolist()

# Ergebnis speichern
output_path = f'./{args.input_dir}/{args.filename}.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(final_data, f, indent=2)

print(f'Combined result written to: {output_path}')

for file in directory.glob(f"{args.filename}_*.part"):
    file.unlink()

# remove parts directory
try:
    os.rmdir(directory_path)
except OSError:
    pass

print(f'Partial files deleted.')
