import json
import re
import pdb

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
        non_functions = ["and", "or" , "if", "elif"]
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

function_calls, function_defs = {"line_num":[], "functions":[]}, {"line_num":[], "functions":[]}

print("Function Calls")
        
for num, cat in enumerate(categorizations):
    if cat['func_call']: # 0 is false
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
                    "is associated with the function def on line number %s\n" %  function_defs["line_num"][i]
                )
                break
        else:
            no_matches_found += 1
print("\n%s function calls did not find a function definition" % (no_matches_found))





print("Blocks")

block_levels = []
indentation_level = []
block_level = 0
block_content = {}
# You go up then you open up new blocks. You go down and you lose blocks
# Yes, this for loop and the other for loops could be combined to reduce the amount of code.
# This one categorizes the block by unique integer identifier. We could also identify it by how far into the code it is.
# This was put aside bc the use case needed to be developed to understand which solution we want to do.
# The two possible solutions that I'm debating are: a tree with child parent nodes, or a double categorization with unique identifiers for each node, and code level. We probably want the tree structure, but I am non-commital. The double categorization will be a problem bc you will still need to calculate the blocks that are related.  


for index, cat in enumerate(categorizations):
    previous_indentation_level =categorizations[index-1]['indentation_level']
    
    # May want to do something different with both cases: TODO
    if index == 0:
        indentation_level.append(0)
        block_content["0"] = [cat['line'].strip()]
        print("starting Block 0")
        print(cat['line'].strip())
        continue
    if cat['indentation_level'] < 0:
        continue
    if cat['empty']:
        continue
    
    if cat['indentation_level'] > indentation_level[-1]:
        indentation_level.append(cat['indentation_level'])
        block_level +=1
        block_content[str(block_level)] = [cat['line'].strip()]
        block_levels.append(block_level)
        
    elif cat['indentation_level'] < indentation_level[-1]:
        indentation_level.pop()
        block_levels.pop()
        indent_index = indentation_level.index(cat['indentation_level'])
        for i in range(len(indentation_level) - 1 - indent_index):
            indentation_level.pop()
            block_levels.pop()
            #TODO deal with repeats
        if len(indentation_level) == 1:
            print("back to previous block %s" % (0))
            block_content["0"].append(cat['line'].strip())
        else:
            block_content[str(block_levels[-1])].append(cat['line'].strip())      
    elif cat['indentation_level'] == indentation_level[-1]:
        if len(block_levels) == 0:
            block_content[str(0)].append(cat['line'].strip())
        else:
            block_content[str(block_levels[-1])].append(cat['line'].strip())

for i in block_content:
    print(i)
    for j in block_content[i]:
        print(j)
