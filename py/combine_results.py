import numpy as np
import argparse
import json
import sys
import os

TODO: This is unfinished business

parser = argparse.ArgumentParser(description='This script computes stable kappa values for CMA.')
parser.add_argument('input_dir', type=str, help='Input directory name')
parser.add_argument('--output', type=str, help='Output file name', default='4_drift_results.json')
parser.add_argument('--exploration_grid', type=str, help='Exploration grid file name', default='1_grid.txt')
parser.add_argument('--terms', type=str, help='Comma separated terms', default='1,2')
parser.add_argument('--base_term', type=str, help='The base term that norms the thing', default="0")
parser.add_argument('--iterations', type=str, help='iterations to find the best value', default='3')
args = parser.parse_args()

data = []
for filename in os.listdir(directory_path):
    if filename.endswith('.json'):
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