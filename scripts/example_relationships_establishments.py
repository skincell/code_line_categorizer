import json
import re
import pdb

def extract_function_name(line):
    functions = []
    # Search for patterns which indicate function calls
    results = re.findall("(.\w+\s|.\w+)[(]", line)
    if results == None:
        return
    for result in results:
        continue_on_result = False
        
        # Makes sure that the function isn't because of a keyword
        # i.e example elif (x = 1 or y = 1) and (blah == 1)
        keywords = ["and", "or" , "if", "elif"]
        for keyword in keywords:
            if keyword in line:
                # Checks to see whether the instance of the keyword is at the start of a variable/function name. 
                secondary_results = re.search( "\s" + keyword, line)
                if secondary_results == None:
                    continue
                for second_result in secondary_results.regs:
                    # Checks whether the keyword is the same before the possible function
                    if second_result[1]-1 == result[0]:
                        continue_on_result = True
                            
        if continue_on_result:
            continue
        # TODO check to see if the function is within a string
        if len(result) == 0:
            continue
        elif result[0] == "." or result[0] == " ":
            functions.append(result[1:])
        else:
            print("How did this happen??")
            functions.append(result[0:])
    return functions

                
with open("../data/outputs/categorizer_cat_output.json") as fp:
    categorizations = json.load(fp)

function_calls, function_defs = {"line_num":[], "functions":[]}, {"line_num":[], "functions":[]}

print("Function Calls")
        
for num, cat in enumerate(categorizations):
    if cat['func_call'] == 1:
        cat["functions"] = extract_function_name(cat["line"])
        print(num)
        print(cat["functions"])
        function_calls["line_num"].append(num)
        function_calls["functions"].append(cat["functions"])
        
print("Function defs")
for num, cat in enumerate(categorizations):
    if cat['func_def'] == 1:
        cat["function_defs"] = extract_function_name(cat["line"])
        print(num)
        print(cat["function_defs"])
        function_defs["line_num"].append(num)
        function_defs["functions"].extend(cat["function_defs"])

count_non_found_functions = 0
for index, function_list in enumerate(function_calls["functions"]):
    for function in function_list:
        for i in range(len(function_defs["line_num"])):
            if function_defs["functions"][i] == function:
                print(
                    "Function call %s on line number %s " % (function, function_calls["line_num"][index]) +
                    "is associated with the function def on line number %s" %  function_defs["line_num"][i]
                )
                print("")
                break
        else:
            count_non_found_functions += 1
print()            
print("%s function calls did not find the function defs" % (count_non_found_functions))
