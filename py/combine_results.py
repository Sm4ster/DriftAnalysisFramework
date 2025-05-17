import numpy as np
import argparse
import json
import os

parser = argparse.ArgumentParser(description='This script computes stable kappa values for CMA.')
parser.add_argument('input_dir', type=str, help='Input directory name')
args = parser.parse_args()

directory_path = f'./data/{args.input_dir}/part_results/'

data = []
for filename in os.listdir(directory_path):
    filepath = os.path.join(directory_path, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data.append(json.load(f))


def combine_nan_arrays(arrays):
    if not arrays:
        raise ValueError("No arrays provided.")

    result = np.copy(arrays[0])
    for arr in arrays[1:]:
        result = np.where(np.isnan(result), arr, result)
    return result


# Initialisierung
keys = ['drift', 'standard_deviation', 'success', 'precision', 'success_mean', 'success_std', 'no_success_mean',
        'no_success_std']
combined = {key: [] for key in keys}
meta = None

final_data = {}

# Dateien laden
for i, filename in enumerate(sorted(os.listdir(directory_path))):
    filepath = os.path.join(directory_path, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)
    if i == 0: final_data = content
    for key in keys:
        array = np.array(content[key])
        combined[key].append(array)

# Arrays kombinieren
for key in keys:
    combined_array = combine_nan_arrays(combined[key])
    final_data[key] = combined_array.tolist()

# Ergebnis speichern
output_path = f'./data/{args.input_dir}/1_result.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(final_data, f, indent=2)

print(f'Combined result written to: {output_path}')
