import sys
import json
import argparse
import os
from fractions import Fraction
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, rgb2hex

def value_to_hex(value, vmin, vmax, cmap_name='viridis'):
    """
    Maps a value to a hex color code based on a colormap.

    Parameters:
        value (float): The value to map to a color.
        vmin (float): The minimum value of the data range.
        vmax (float): The maximum value of the data range.
        cmap_name (str): Name of the colormap to use (default: 'viridis').

    Returns:
        str: The hex color code.
    """
    if vmin == vmax:
        return "ffffff"  # White if there's no range

    norm = Normalize(vmin=vmin, vmax=vmax)
    normalized_value = norm(value)
    cmap = plt.cm.get_cmap(cmap_name)
    rgba = cmap(normalized_value)
    return rgb2hex(rgba[:3])[1:]  # Remove '#' to fit LaTeX command

def text_color_for_hex(hex_color):
    """ Returns 'black' or 'white' depending on brightness of the background color """
    r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    brightness = (r * 299 + g * 587 + b * 114) / 1000  # Luminance formula
    return "black" if brightness > 128 else "white"


# Argument parser
parser = argparse.ArgumentParser(description='This script makes a heatmap-like table for LaTeX.')
parser.add_argument('input_dir', type=str, help='Input directory name')
args = parser.parse_args()

input_path = f"./data/{args.input_dir}/"
json_file = input_path + "4_drift_results.json"

# Ensure the JSON file exists
if not os.path.exists(json_file):
    print(f"Error: File {json_file} not found.")
    sys.exit(1)

# Load data
data = json.load(open(json_file))

# Extract unique sorted factor lists
factor_1_list = sorted(set(el["factors"][0] for el in data))
factor_2_list = sorted(set(el["factors"][1] for el in data))

def make_table(attribute):
    # Compute color scale range
    drift_values = [item[attribute] for item in data]
    vmin, vmax = min(drift_values), max(drift_values)

    # Find value where factors are (1,1)
    value_11 = next((item[attribute] for item in data if item["factors"] == [1, 1]), None)

    with open(output_file, "a") as file:
        file.write(f"\\begin{{table}}[h]\n%\\caption{{ {attribute} (base_value) = {value_11}}}\n\\begin{{center}}\n\\renewcommand{{\\arraystretch}}{{1.5}}\n")

        insert = " ".join(["c"] * len(factor_2_list))
        file.write(f"\\begin{{tabular}}{{lr {insert} }}\n")

        file.write("\\toprule\n")
        file.write(f"& & \multicolumn{{{len(factor_2_list)}}}{{c}}{{\\large{{$\\boldsymbol{{d}}$}}}} \\\\\n")

        # Table column headers
        headers = []
        for factor_2 in factor_2_list:
            if factor_2 < 1:
                fraction = Fraction(round(factor_2, 10)).limit_denominator()
                headers.append(f"$\\sfrac{{{fraction.numerator}}}{{{fraction.denominator}}}$")
            else:
                headers.append(str(round(factor_2, 10)))

        file.write("& & " + " & ".join(headers) + " \\\\\n")

        file.write("\\midrule\n")
        file.write(f"\\multirow{{{len(factor_1_list)}}}[0]{{*}}{{\\begin{{sideways}}\\large{{$\\boldsymbol{{c_{{cov}}}}$}}\\end{{sideways}}}}\n")

        # Table rows
        for factor_1 in factor_1_list:
            row = []
            if factor_1 < 1:
                fraction = Fraction(round(factor_1, 10)).limit_denominator()
                row.append(f"$\\sfrac{{{fraction.numerator}}}{{{fraction.denominator}}}$")
            else:
                row.append(str(round(factor_1, 10)))

            element_sublist = [item for item in data if item["factors"][0] == factor_1]

            for factor_2 in factor_2_list:
                element = next((item for item in element_sublist if item["factors"][1] == factor_2), None)
                value = element[attribute] if element else None
                color = value_to_hex(value if value is not None else vmin, vmin, vmax)
                row.append(f"\\hexc{{{color}}}" + (f" \\textcolor{{{text_color_for_hex(color)}}} {{{round((value / value_11), 3)}}}" if value is not None else " "))

            file.write("& " + " & ".join(row) + " \\\\\n")

        file.write("\\bottomrule\n\\end{tabular}\n\\end{center}\n%\label{table:TABLEREF}\n\\end{table}\n")

# Output file
output_file = input_path + "5_tables"

with open(output_file, "w") as file:
    file.write("% % %\n")

make_table("smallest_drift")
make_table("v_1")
make_table("v_2")

