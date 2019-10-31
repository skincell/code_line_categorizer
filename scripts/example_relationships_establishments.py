import json
import re
import pdb
import ast


def extract_function_name(line):

    functions = []

    # Search for patterns which indicate function calls
    function_name_candidates = re.findall("(.\w+\s|.\w+)[(]", line)
    if function_name_candidates == None:
        return
    for func_name_candidate in function_name_candidates:
        non_function_confirmed = False

        # Makes sure that the function isn't because of a non_function
        # i.e example elif (x = 1 or y = 1) and (blah == 1)
        non_functions = ["and", "or", "if", "elif"]
        for non_function in non_functions:
            if non_function in func_name_candidate:
                # Checks to see whether the instance of the non_function is part of a variable/function name.
                if non_function.strip() != func_name_candidate.strip().strip("."):
                    continue
                else:
                    non_function_confirmed = True
                    break

        if non_function_confirmed:
            continue

        # TODO check to see if the function is within a string
        if len(func_name_candidate) == 0:
            continue
        else:
            functions.append(func_name_candidate[0:].strip().strip("."))
    return functions


with open("../data/outputs/categorizer_cat_output.json") as fp:
    categorizations = json.load(fp)

function_calls, function_defs = {"line_num": [], "functions": []}, {
    "line_num": [], "functions": []}

print("Function Calls")

for num, cat in enumerate(categorizations):
    if cat['func_call']:  # 0 is false
        cat["functions"] = extract_function_name(cat["line"])
        function_calls["line_num"].append(num)
        function_calls["functions"].append(cat["functions"])

print("Function defs")
for num, cat in enumerate(categorizations):
    if cat['func_def']:
        cat["function_defs"] = extract_function_name(cat["line"])
        function_defs["line_num"].append(num)
        function_defs["functions"].extend(cat["function_defs"])

no_matches_found = 0
for index, function_list in enumerate(function_calls["functions"]):
    for function in function_list:
        for i in range(len(function_defs["line_num"])):
            if function_defs["functions"][i] == function:
                print(
                    "Function call %s on line number %s " % (function, function_calls["line_num"][index]) +
                    "is associated with the function def on line number %s\n" % function_defs[
                        "line_num"][i]
                )
                break
        else:
            no_matches_found += 1
print("\n%s function calls did not find a function definition" %
      (no_matches_found))


r = open("./categorizer.py", "r")
t = ast.parse(r.read())
for i in ast.iter_child_nodes(t):
    print(i)
    for j in ast.iter_fields(i):
        print(j)
    print()
    pdb.set_trace()

"""
for cat in categorizations:
    print(cat)
    if cat["func_def"] == 0 and cat["conditional"] == 0 and cat["comment"] != 1:
        ast_node = ast.parse(cat["line"])
        print(ast.dump(ast_node))
"""
