import sys
import json
import argparse
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
    # Normalize the value
    norm = Normalize(vmin=vmin, vmax=vmax)

    normalized_value = norm(value)

    # Get the colormap
    cmap = plt.cm.get_cmap(cmap_name)

    # Map the normalized value to RGBA and convert to hex
    rgba = cmap(normalized_value)
    hex_color = rgb2hex(rgba[:3])  # Use only the RGB part

    return hex_color[1:]

parser = argparse.ArgumentParser(description='This script makes a heatmap like table for latex.')
parser.add_argument('input_dir', type=str, help='Input directory name')
args = parser.parse_args()

input_path = "./data/" + args.input_dir + "/"


data = json.load(open(input_path + "4_drift_results.json"))
factor_1_list = sorted(set([el["factors"][0] for el in data]))
factor_2_list = sorted(set([el["factors"][1] for el in data]))

vmin = min([item["smallest_drift"] for item in data])
vmax = max([item["smallest_drift"] for item in data])

#TODO Colorscales to insert

with open(input_path + "5_tables", "w") as file:
    sys.stdout = file

    print("\\begin{table}[h]\n%\\caption{CAPTION}\n\\begin{center}\n\\renewcommand{\\arraystretch}{1.5}")
    insert = " ".join(["c"] * len(factor_2_list))
    print(f"\\begin{{tabular}}{{lr {insert} }}")

    print("\\toprule")
    print(f"& & \multicolumn{{{len(factor_2_list)}}}{{c}}{{\large{{$\\boldsymbol{{c_{{cov}}}}$}}}} \\\\")

    insert = ""
    for factor_2 in factor_2_list:
        if factor_2 < 1:
            fraction = Fraction(round(factor_2, 10)).limit_denominator()
            insert += f"& $\\sfrac{{{fraction.numerator}}}{{{fraction.denominator}}}$"
        else:
            insert += "& " + str(round(factor_2, 10))

    print(f"& {insert} \\\\")

    print("\\midrule")
    print(f"\multirow{{{len(factor_1_list)}}}[0]{{*}}{{\\begin{{sideways}}\large{{$\\boldsymbol{{c_{{\\sigma}}}}$}}\\end{{sideways}}}}")

    for factor_1 in factor_1_list:
        row = "& " + str(round(factor_1, 10))
        if factor_1 < 1:
            fraction = Fraction(round(factor_1,10)).limit_denominator()
            row = f"& $\\sfrac{{{fraction.numerator}}}{{{fraction.denominator}}}$"
        element_sublist = [item for item in data if item["factors"][0] == factor_1]
        for factor_2 in factor_2_list:
            element = [item for item in element_sublist if item["factors"][1] == factor_2]
            value = element[0]["smallest_drift"] if len(element) > 0 else 0
            color = value_to_hex(value, vmin, vmax)
            row += " & \\hexc{" + color + "}" + (("{" + str(round(value, 5)) + "}") if len(element) > 0 else "     ")
        print(row + " \\\\")

    print("\\bottomrule\n\\end{tabular}\n\\end{center}\n%\label{table:TABLEREF}\n\\end{table}")

    # Reset to default
    sys.stdout = sys.__stdout__  # Reset to default


