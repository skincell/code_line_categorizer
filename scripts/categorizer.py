
# All standard libraries
import collections
import re
import hashlib
import json
import os

# TODO redo earlier sections with new found knowledge.

def find_empty_lines(line):
    """
    Returns 1 for an empty line and 0 for non-empty
    :param line:
    :return:
    """

    if line.strip("\t").strip(" ").strip("\n") == '':
        return 1

    return 0

def determine_if_conditional(line_number, multiline_number, line, categorizations):
    """
    Determines if the line has a conditional associated with it.

    :param line_number:
    :param multiline_number:
    :param line:
    :param categorizations:
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

    if line_number != 0:
        if categorizations[line_number-1].multiline_statement_number and multiline_number:
            if categorizations[line_number-1].conditional:
                return 1

    return 0

def determine_if_assignment(line_number, multiline_number, line,
                            categorizations, function_def):
    """
    Determines if the line has an assignment associated with it.

    :param line_number:
    :param multiline_number:
    :param line:
    :param categorizations:
    :return:
    """
    # Looks for assignments that are from passing in variables from defs
    if function_def:
        if multiline_number:
            # I want to eventually want to check in between the first and last line to make sure assignments occur
            # But I'm assuming right now that you won't do the following
            # def function_blah(
            #                    )
            return 1
        else:
            # https://stackoverflow.com/questions/4894069/regular-expression-to-return-text-between-parenthesis
            if len(line[line.find("("):line.rfind(")")].strip()) > 0:
                return 1

        # no assignments are in parameters in this line
        return 0

    # Checks for assignments using the equal sign
    if "=" in line:
        assignment_match_list = ["[^=^!^>^<][=](\s|\w|\s\w)"]
        for assignment_match in assignment_match_list:
            results = re.search(assignment_match, line)
            if results != None:
                for result in results.regs:
                    if not check_if_in_string(line, result[0]):
                        return 1

    # Checks for an assignment that goes through multiple lines
    if line_number != 0:
        if categorizations[line_number-1].multiline_statement_number and multiline_number:
            if categorizations[line_number-1].assignment:
                return 1

    return 0


def determine_if_function_def(line_number, multiline_number, line, categorizations):
    """
    Determines if the line has a function_def associated with it.

    :param line_number:
    :param multiline_number:
    :param line:
    :param categorizations:
    :return:
    """
    if "def" in line:
        # Don't need to check to see if "if" is in string as the first check wouldn't work if it was
        if re.search("def\s", line.strip(" ")[0:4]) != None:
            return 1

    if line_number != 0:
        if categorizations[line_number-1].multiline_statement_number and multiline_number:
            if categorizations[line_number-1].func_def:
                return 1

    return 0

def determine_if_function_call(line_number, multiline_number, line, categorizations):
    """
    Determines if the line has a function associated with it.

    :param line_number:
    :param multiline_number:
    :param line:
    :param categorizations:
    :return:
    """
    # Checking if the line is a not a function def.
    if "def" not in line or re.search("def\s", line.strip(" ")[0:4]) == None:
        # Search for patterns which indicate function calls
        results = re.search("(\w\s|\w)[(]", line)
        if results != None:
            for result in results.regs:
                if not check_if_in_string(line, result[0]):
                    return 1

    if line_number != 0:
        if categorizations[line_number-1].multiline_statement_number and multiline_number:
            if categorizations[line_number-1].func_call:
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

def main():
    """
    Currently this function does some prescripted stuff.

    :return:
    """
    output_log = []
    with open("./categorizer.py") as fp:
        # This scope is bothering me
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

    LineAndCats = collections.namedtuple('LineAndCats', 'line multiline_statement_number comment conditional empty func_def assignment func_call')
    # https://stackoverflow.com/questions/11351032/namedtuple-and-default-values-for-optional-keyword-arguments
    LineAndCats.__new__.__defaults__ = (0,) * len(LineAndCats._fields)

    # Categorizing lines
    for line_number, line in enumerate(lines):

        multiline_number = multilines[line_number]
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
        is_conditional = determine_if_conditional(line_number, multiline_number, line, categorizations) # This might be an exclusive one
        is_function_def = determine_if_function_def(line_number, multiline_number, line, categorizations)
        is_assignment = determine_if_assignment(line_number, multiline_number, line, categorizations, is_function_def)
        is_function_call = determine_if_function_call(line_number, multiline_number, line, categorizations)

        categorizations.append(LineAndCats(line, multiline_statement_number=multilines[line_number],
                                           conditional=is_conditional, func_def=is_function_def,
                                           assignment=is_assignment, func_call= is_function_call))


        hash_object = hashlib.md5((line + " " + str(line_number)).encode())

        # Create a string which tracks line classfications/categorizations to store in hash
        line_and_classifications = ""
        for number in range(len(LineAndCats._fields)):
            line_and_classifications += " " +  "%s " % (LineAndCats._fields[number]) + str(categorizations[-1][number])

        hash_storage[hash_object.hexdigest()] = line_and_classifications

    # Debug portion -> maybe have all of theese produced into folders when ran???
    print_file_cats(lines, "func_call", categorizations)

    print("Uncategorized LInes")

    uncat_storage = {}
    # TODO change editor background to be more friendly with black
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

    changed_line_classification = False

    # Compares old hashes to new hashes to see if any categorization has changed for any line.
    if os.path.isfile("../data/outputs/hash_storage.json"):
        with open("../data/outputs/hash_storage.json", 'r') as fp:
            previous_hash_storage = json.load(fp)
            for hash in previous_hash_storage:
                if hash in hash_storage:

                    # Want to see if any categorization for a line has changed.
                    # Do not care if only line has changed and no change in categorizations -> this is already taken care of implicitly
                    # Do care if line doesn't change but categorizations do.
                    if hash_storage[hash] not in previous_hash_storage[hash]:
                        line_end_index = hash_storage[hash].index("\n")
                        index_of_line = hash_storage[hash].index("line")
                        
                        string_1 = previous_hash_storage[hash]
                        string_2 = hash_storage[hash]

                        # TODO debate whether you should change this to instead use the line categorization structure instead
                        indices_of_differences = [i for i in xrange(len(string_1)) if string_1[i] != string_2[i]]

                        print("Changed Categorization line \n %s " % (string_1[index_of_line+4:line_end_index]).strip())
                        for index in indices_of_differences:

                            index_1 = string_1.rfind(" ", 0, index - 2)
                            print("Categorization " + string_1[index_1:index] + " changed from " + string_1[index] + " to " + string_2[index])

                        changed_line_classification = True


    # Compares old hashes to new hashes to see when something goes from uncat storage to categorized storage.
    if os.path.isfile("../data/outputs/uncat_storage.json"):
        with open("../data/outputs/uncat_storage.json", 'r') as fp:
            previous_hash_storage = json.load(fp)
            for hash in previous_hash_storage:
                if hash in hash_storage:

                    # Want to see if any categorization for a line has changed.
                    # Do not care if only line has changed and no change in categorizations -> this is already taken care of implicitly
                    # Do care if line doesn't change but categorizations do.
                    if uncat_storage[hash] not in previous_hash_storage[hash]:
                        print("Uncat Storage")
                        print(previous_hash_storage[hash])
                        print("Now Categorized")
                        print(hash_storage[hash])
                      

    if changed_line_classification:
       exit()

    with open("../data/outputs/hash_storage.json", 'w') as fp:
        json.dump(hash_storage, fp)

    with open("../data/outputs/uncat_hash_storage.json", 'w') as fp:
        json.dump(uncat_storage, fp)

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
    main()
