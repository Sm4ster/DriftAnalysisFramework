import sys
import json
import argparse
from fractions import Fraction

parser = argparse.ArgumentParser(description='This script makes a heatmap like table for latex.')
parser.add_argument('input_dir', type=str, help='Input directory name')
args = parser.parse_args()

input_path = "./data/" + args.input_dir + "/"


data = json.load(open(input_path + "4_drift_results.json"))
factor_1_list = sorted(set([el["factors"][0] for el in data]))
factor_2_list = sorted(set([el["factors"][1] for el in data]))

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
            row += " & " + (str(round(element[0]["smallest_drift"], 3)) if len(element) > 0 else "     ")
        print(row + " \\\\")

    print("\\bottomrule\n\\end{tabular}\n\\end{center}\n%\label{table:TABLEREF}\n\\end{table}")

    # Reset to default
    sys.stdout = sys.__stdout__  # Reset to default


