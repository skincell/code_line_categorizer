

# All standard libraries
import collections
import re
import hashlib
import json
import os
import argparse
import pdb

# TODO redo earlier sections with new found knowledge.

def compare_new_to_old_hashes(new_hash_storage, old_hash_file_path):
    """

    :param new_hash_storage:
    :param old_hash_file_path:
    :return:
    """

    changed_line_classification = False

    # Compares old hashes to new hashes to see if any categorization has changed for any line.
    if os.path.isfile(old_hash_file_path):
        with open(old_hash_file_path, 'r') as fp:
            previous_hash_storage = json.load(fp)
            for script_line_hash in previous_hash_storage:
                if script_line_hash in new_hash_storage:

                    # Want to see if any categorization for a line has changed.
                    # Do not care if only line has changed and no change in categorizations -> this is already taken care of implicitly
                    # Do care if line doesn't change but categorizations do.
                    if new_hash_storage[script_line_hash] not in previous_hash_storage[script_line_hash]:
                        line_end_index = new_hash_storage[script_line_hash].index("\n")
                        index_of_line = new_hash_storage[script_line_hash].index("line")

                        string_1 = previous_hash_storage[script_line_hash]
                        string_2 = new_hash_storage[script_line_hash]

                        indices_of_differences = [i for i in range(len(string_1)) if string_1[i] != string_2[i]]

                        print(
                            "Changed Categorization line \n %s " % (string_1[index_of_line + 4:line_end_index]).strip())
                        for index in indices_of_differences:
                            index_1 = string_1.rfind(" ", 0, index - 2)
                            print("Categorization " + string_1[index_1:index] + " changed from " + string_1[
                                index] + " to " + string_2[index])

                        changed_line_classification = True
    else:
        changed_line_classification = False

    return changed_line_classification

def find_empty_lines(line):
    """
    Returns 1 for an empty line and 0 for non-empty
    :param line:
    :return:
    """

    if line.strip("\t").strip(" ").strip("\n") == '':
        return 1

    return 0

def determine_if_conditional(line):
    """
    Determines if the line has a conditional associated with it.

    :param line:
    :return:
    """
    if "if" in line or "else" in line:
        # Don't need to check to see if "if" is in string as the first check wouldn't work if it was
        if re.search("if\s", line.strip(" ")[0:3]) != None:
            return 1
        # The level up check for "else" ensures that there will be no index out of bounds bug
        elif re.search("elif\s", line.strip(" ")[0:5]) != None:
            return 1
        elif re.search("else:", line.strip(" ")[0:5]) != None:
            return 1

    return 0

def determine_if_equal_sign_assignment(line):

    """
    Determines if the line has an assignment associated with it.

    :param line:
    :return:
    """

    # Checks for assignments using the equal sign
    if "=" in line:
        assignment_match_list = ["[^=^!^>^<][=](\s|\w|\s\w)"]
        for assignment_match in assignment_match_list:
            results = re.search(assignment_match, line)
            if results != None:
                for result in results.regs:
                    if not check_if_in_string(line, result[0]):
                        return 1

    return 0

def determine_indentation_level(line):
    """
    Determines the indent level of the line. This only works properly if either all tabs or spaces are used.
    """
    
    indent_level = re.search("\w", line)
    if indent_level.regs is not None:
        return indent_level.regs[0][0]

    return 0

def determine_if_function_def(line):
    """
    Determines if the line has a function_def associated with it.

    :param line:
    :return:
    """
    if "def" in line:
        # Don't need to check to see if "if" is in string as the first check wouldn't work if it was
        if re.search("def\s", line.strip(" ")[0:4]) != None:
            return 1

    return 0

def determine_if_function_call(line):
    """
    Determines if the line has a function associated with it.

    :param line:
    :return:
    """

    # Checking if the line is a not a function def.
    if "def" not in line or re.search("def\s", line.strip(" ")[0:4]) == None:

        function_name_candidates = re.findall("(.\w+\s|.\w+)[(]", line)
        if function_name_candidates == None:
            return 0
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
            elif not check_if_in_string(line, line.index(func_name_candidate)):
                return 1

    return 0

def find_comment_lines(lines):
    """
    Categorizes comment lines, assigning a 0 or 1 depending on whether a comment is present or not.
    Comment categorization is important, so we can remove them from code categorization of lines.
    This code block is odd in the sense that a hybrid type of categorization is actually done.
    It handles multi-lined comments which simplifies the multi-line categorization, but it breaks the philophsy that
    is being used to make a single function = single categorization.

    :param line:
    :return:
    """

    comment_lines = []
    multiline_comment = False
    for line in lines:

        # Checks for a regular comment
        if line.strip(" ").strip("\t")[0] == "#":
             comment_lines.append(1)
             continue

        # Checks for multiline comment start or end
        elif ("\"\"\"" in line or "'''" in line) \
            and "if" not in line:
            # ["if" not in line]^ is a hack that can come back to hurt the project.

            comment_lines.append(1)

            # Closes or opens a multi line comment block
            if multiline_comment:
                multiline_comment = False
            else:
                multiline_comment = True

            continue

        # Part of a multi line comment
        if multiline_comment:
            comment_lines.append(1)
            continue

        # Default case, if it hits nothing else then it appends a zero
        comment_lines.append(0)

    return comment_lines

def strip_comments_after_code(lines, comment_lines):
    """
    Strips comments from lines which are not comment lines. This function is used to simplify logic down below.
    This function changes the lines variable.

    :param lines:
    :param comment_lines:
    :return:
    """
    for line_number, line in enumerate(lines):
        # if a comment line, no modifications are needed.
        if comment_lines[line_number] == 1:
            continue

        # This will be overwritten in while loop
        comment_symbol_index = 0

        # copy of the line
        string_to_search = line
        # Figuring out whether there is a comment char not in a string
        while comment_symbol_index != None:

            # Try to find if a comment exists on code line
            try:
                comment_symbol_index = string_to_search.index("#")
            except ValueError:
                comment_symbol_index = None

            if comment_symbol_index != None:

                if not check_if_in_string(line, comment_symbol_index):
                    # inline comments are removed from lines to reduce categorization complexity
                    lines[line_number] = line[0:comment_symbol_index]  # Should disappear inline comments from the analyzer
                    break

                # string_to_search is only for finding multiple # not for using in the quotation balancing
                string_to_search = line[comment_symbol_index + 1:]

def check_if_in_string(line, index_to_check):
    #TODO we use and will be using this function a lot; see if there is a way to reduce runtime in function.
    """
    Function determines if the index that you are trying to identify is in a string or not.
    This is useful in identifying whether your variable is an actual categorization or a false positive.
    It does this by counting quotations before the index to determine if the quotations are unbalanced hence an open string.

    :param line:
    :param index_to_check:
    :return:
    """
    # Trying to capture the excpetion that a # in is in a string rather than after code on a line
    before_counter = 0
    after_counter = 0
    # Empty string
    last_quotation = ''
    # Tries to find the before and after balance of quotations.
    # There is probably an imbalance with \" or ' might be weird.
    for char_index, char in enumerate(line):

        # Check for a quotation character first
        if "\"" in char or ("'" in char):
            if char_index != 0:

                # Pass over the cases that a quotation is inside a quotation.
                if line[char_index - 1] == "\\" or \
                        ("\'" in char and before_counter % 2 == 1 and "\"" in last_quotation):
                    continue
                else:

                    # Counts quotation marks before current character
                    # Also tracks which quotation mark was the most recent openned one
                    if char_index < index_to_check:
                        before_counter += 1

                        # Tracks the type of the last open quotation mark used
                        if before_counter % 2 == 1:
                            last_quotation = char
                        else:
                            # Assigns an empty string
                            last_quotation = ''

                    # Currently we do not use the after counter
                    else:
                        after_counter += 1
            else:
                before_counter += 1

    # You are not in a string
    if before_counter % 2 == 0:
        return False
    else:
        return True

def multiline_lines(lines, comment_lines):
    """
    Makes a data structure which tracks whether a code statement spans several lines, and numbers each multi-line group.

    Used https://www.techbeamers.com/understand-python-statement-indentation/#how-to-use-multiline-statement
    as a guide to what type of multi-line exists

    :param lines:
    :return: * **multiline_statements** : a list which has a 0 for a line number which corresponds to no multiline activity
                                and a number corresponding to its grouping of multi-lines, so a multi-line statement may
                                be labeled 3 across four lines.
    """

    enclosure_stack = []
    multiline_statements = len(lines) * [None]
    continuation_line = False
    multiline_statement_number = 1

    for line_number, line in enumerate(lines):

        # Checks to see if comment line
        if comment_lines[line_number]:
            multiline_statements[line_number] = 0
            continue

        # closures stack algorithmn
        for char_index, char in enumerate(line):

            if char == "(":
                # Checks to see if the enclosure is not in a string
                if not check_if_in_string(line, char_index):
                    enclosure_stack.append('(')
            elif char == ")":
                # This check must occur after the above check as this is not ensured to work on quotations
                if not check_if_in_string(line,
                                          char_index):
                    enclosure_stack.pop()
            elif char == "{":
                if not check_if_in_string(line, char_index):
                    enclosure_stack.append('{')
            elif char == "}":
                if not check_if_in_string(line, char_index):
                    enclosure_stack.pop()
            elif char == "[":
                if not check_if_in_string(line, char_index):
                    enclosure_stack.append('[')
            elif char == "]":
                if not check_if_in_string(line, char_index):
                    enclosure_stack.pop()

        #  parenthesis or another closure still open makes this multi-lined
        if enclosure_stack:
            multiline_statements[line_number] = multiline_statement_number
            continuation_line = True
            continue

        # Checks for the explicit multi-line character
        elif len(line.strip(" ").strip("\n")) > 0 and line.strip(" ").strip("\n")[-1] == "\\":
            multiline_statements[line_number] = multiline_statement_number
            continuation_line = True
            continue

        # If the previous line was multi but no signals for more multi-occurs.
        if continuation_line:
            multiline_statements[line_number] = multiline_statement_number
            continuation_line = False

            # increment the multi_line_numberings
            multiline_statement_number += 1
            continue

        # Design note: any more conditionals for multi-line need a continue statement for this logic to work.

        # Default case if not multi-lined
        multiline_statements[line_number] = 0

    return multiline_statements

def main(args):
    """
    Currently this function does some prescripted stuff.

    :return:
    """

    with open(args.file_path) as fp:
        lines = fp.readlines()

    """
    Pre-processing and other categorizations
    """
    # Categorize and labels comment lines without code
    comment_lines = find_comment_lines(lines)
    # Gets rid of inlined comments
    strip_comments_after_code(lines, comment_lines)
    # Categorizes multi-lined systems
    multilines = multiline_lines(lines, comment_lines)

    categorizations = []
    hash_storage = {}

    # Add a new category here when added
    LineAndCats = collections.namedtuple('LineAndCats', 'line multiline_statement_number comment conditional empty func_def equal_sign_assignment func_call indentation_level')
    
    # https://stackoverflow.com/questions/11351032/namedtuple-and-default-values-for-optional-keyword-arguments
    LineAndCats.__new__.__defaults__ = (0,) * len(LineAndCats._fields)

    # Categorizing lines
    for line_number, line in enumerate(lines):

        multiline_number = multilines[line_number]
        # Logic to carry over what happened to the current line

        # TODO Want to start categorizing this based on whether it is a multi-line conditional, function_call, function_def, and determine which one it is rather than just reassigning everything
        if line_number != 0:
            if categorizations[line_number - 1].multiline_statement_number and multiline_number:
                categorizations.append(
                                       LineAndCats(
                                           line, multiline_statement_number=multilines[line_number],
                                           conditional=is_conditional, func_def=is_function_def,
                                           equal_sign_assignment=is_equal_sign_assignment, func_call=is_function_call,
                                           indentation_level=categorizations[line_number - 1].indentation_level
                                       )
                )
                continue
        """
        Exclusive categorization
        """
        # Skip over if comment lines... we might need to rethink this, but it avoids problems in categorizing the rest..
        if comment_lines[line_number]:
            categorizations.append(LineAndCats(line, comment=1))
            continue

        is_empty = find_empty_lines(line)
        # Another exclusive trait of a line
        if is_empty:
            categorizations.append(LineAndCats(line, empty=1))
            continue


        """
        Inclusive categorizations
        """
        # Categorizing
        is_conditional = determine_if_conditional(line) # This might be an exclusive one
        is_function_def = determine_if_function_def(line)
        is_equal_sign_assignment = determine_if_equal_sign_assignment(line)
        is_function_call = determine_if_function_call(line)
        indentation_level = determine_indentation_level(line)

        # TODO try to figure out if you can use keyword arguments
        categorizations.append(
                               LineAndCats(
                                           line, multiline_statement_number=multilines[line_number],
                                           conditional=is_conditional, func_def=is_function_def,
                                           equal_sign_assignment=is_equal_sign_assignment,
                                           func_call=is_function_call, indentation_level=indentation_level
                               )
        )


        hash_object = hashlib.md5((line + " " + str(line_number)).encode())

        # Create a string which tracks line classfications/categorizations to store in hash
        line_and_classifications = ""
        for number in range(len(LineAndCats._fields)):
            line_and_classifications += " " +  "%s " % (LineAndCats._fields[number]) + str(categorizations[-1][number])

        hash_storage[hash_object.hexdigest()] = line_and_classifications

    # Debug portion -> maybe have all of theese produced into folders when ran???
    print_file_cats(lines, "indentation_level", categorizations)

    print("Uncategorized Lines")

    uncat_storage = {}
    # Print out lines which are not categorized as anything yet..
    for cat in categorizations:
        for cat_index in range(1, len(LineAndCats._fields)):
            # Checks whether there is a categorization
            if cat[cat_index]:
                break
        else:
            print(cat[0].strip("\n"))
            hash_object = hashlib.md5((line + " " + str(line_number)).encode())
            uncat_storage[hash_object.hexdigest()] = line

    # Changed categorization lines
    hash_file_path = "../data/outputs/hash_storage.json"
    changed_line_classification = compare_new_to_old_hashes(hash_storage, hash_file_path)

    print("Newly Categorized")
    # Going from uncategorized to categorized
    hash_file_path = "../data/outputs/uncat_storage.json"
    _ = compare_new_to_old_hashes(uncat_storage, hash_file_path)

    if changed_line_classification:
        raise NameError("The line(s) have changed classifications.")

    with open("../data/outputs/hash_storage.json", 'w') as fp:
        json.dump(hash_storage, fp)

    with open("../data/outputs/uncat_hash_storage.json", 'w') as fp:
        json.dump(uncat_storage, fp)

    with open("../data/outputs/%s_cat_output.json" % (args.file_path.split("/")[-1].split("/")[-1].split(".")[0]), "w") as fp:
        dict_cat = [0] * len(categorizations)
        for index, cat in enumerate(categorizations):
            # https://gist.github.com/Integralist/b25185f91ebc8a56fe070d499111b447
            dict_cat[index] = cat._asdict()
            
        json.dump(dict_cat, fp)

def print_file_cats(lines, category, categorizations):
    """
    Debug printing

    :param lines:
    :param category:
    :return:
    """
    print(category)
    for line_number, line in enumerate(lines):

        stripped_line = line.strip("\n")
        # Wow if I had assigned a doc string to the variable then I would have had a comment categorization...
        code = "print(str(line_number) + \" \" + str(categorizations[line_number].%s) + \" \" + stripped_line)" % (category)
        exec(code)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Categorizes the lines of code in a single script")
    parser.add_argument("--file_path", default="./categorizer.py", help="File path of file to categorize" )
    main(parser.parse_args())
