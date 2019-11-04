import json
import re
import pdb
import ast

from helper_functions import check_if_in_string


def determine_if_has_variable(var, line):
    # Search for patterns which indicate var presense
    for match_item in re.finditer("[^\w]%s[^\w]" % var, line):
        if check_if_in_string(line, match_item.start() + 1):
            continue
        else:
            return 1
    else:
        return 0


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
print("Function defs")
for num, cat in enumerate(categorizations):

    # check if it is a function def
    if cat['func_def']:
        cat["function_defs"] = extract_function_name(cat["line"])
        function_defs["line_num"].append(num)
        function_defs["functions"].extend(cat["function_defs"])
    # then check if it is a function call
    elif cat['func_call']:  # 0 is false
        cat["functions"] = extract_function_name(cat["line"])
        function_calls["line_num"].append(num)
        function_calls["functions"].append(cat["functions"])
    # Have nothing for a function def which has a function call...
    # I don't want to add this in. Don't make me..

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


# Person inputs these values
variable_to_search_for = "line"
line_number = "461"
cat_index = int(line_number) - 1

# indice of the instances that the variable occurs
variable_instances = []

# Determine all usages of variable
for num, cat in enumerate(categorizations):
    if variable_to_search_for in cat["line"] and \
       not cat["comment"]:
        if_contains_variable = determine_if_has_variable(
            variable_to_search_for, cat["line"])
        if if_contains_variable:
            print("line number %s contains %s," %
                  (num + 1, variable_to_search_for))
            print(cat["line"])
            variable_instances.append(num)


# keep track of two variables, block number and indentation number
# block number is an identifer for this specific block
# indentation number states how far it is nested

print("Blocks")

block_number = [-1] * len(categorizations)
nested_level = [-1] * len(categorizations)
previous_indentation_level = -1
previous_block_number = -1
previous_nested_number = -1
indent_levels = []

for index, cat in enumerate(categorizations):
    # The indentation can be below zero bc it is a comment
    if cat['indentation_level'] < 0:
        continue
    if cat['empty']:
        continue

    pdb.set_trace()
    for i in range(index - 1, 0, -1):
        if categorizations[i]['indentation_level'] != -1 and block_number[i] != -1:
            previous_indentation_level = categorizations[i]['indentation_level']
            previous_block_number = block_number[i]
            previous_nested_number = nested_level[i]
            break

    if cat['indentation_level'] > previous_indentation_level:
        block_number[index] = previous_block_number + 1
        nested_level[index] = previous_nested_number + 1
        indent_levels.append(cat['indentation_level'])

    elif cat['indentation_level'] < previous_indentation_level:
        block_number[index] = previous_block_number + 1
        new_nested_number = indent_levels.index(cat['indentation_level'])
        nested_level[index] = new_nested_number
        indent_levels = indent_levels[:new_nested_number+1]

    else:
        block_number[index] = previous_block_number
        nested_level[index] = previous_nested_number

    print("block level: %s" % (block_number[index]))
    print("nested_level: %s" % (nested_level[index]))
    print("line")
    print(cat["line"])
