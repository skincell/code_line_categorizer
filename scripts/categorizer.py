
def find_empty_lines(line):
    """
    Returns 1 for an empty line and 0 for non-empty
    :param line:
    :return:
    """

    if line.strip("\t").strip(" ").strip("\n") == '':
        return 1

    return 0

def find_comment_lines(lines):
    """
    Tries to categorize comment lines.
    Comment lines are treated as non-code or something that can
    cause false positives for other categorizers.

    Also comments + multi line is a double categorization.
    The design tries to keep categorizations mostly separate from each other,
    but this one breaks that rule. It categorizes multi-line and comments at the same time

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
    Strips comments from lines which are not comment lines

    :param lines:
    :param comment_lines:
    :return:
    """
    for line_number, line in enumerate(lines):
        # if a comment line, no modifications are needed.
        if comment_lines[line_number] == 1:
            continue
        # This will be overwritten in while loop pretty quickly
        comment_line_index = 0
        # copy of the line
        current_line = line
        # Figuring out whether there is a comment char not in a string
        while comment_line_index != None:

            # Try to find if a comment exists on code line
            try:
                comment_line_index = current_line.index("#")
            except ValueError:
                comment_line_index = None

            if comment_line_index != None:

                if not check_if_in_string(line, comment_line_index):
                    # inline comments should not appear when examining this using tools like the one below
                    lines[line_number] = line[0:comment_line_index]  # Should disappear inline comments from the analyzer
                    break

                # current_line is only for finding multiple # not for using in the quotation balancing
                current_line = line[comment_line_index + 1:]

def check_if_in_string(line, index_to_check):

    # copy of line
    # Trying to capture the excpetion that a # in is in a string rather than after code on a line
    before_counter = 0
    after_counter = 0

    last_quotation = ''
    # Tries to find the before and after balance of quotations.
    # There is probably an imbalance with \" or ' might be weird.
    for char_index, char in enumerate(line):

        # Check for a quotation character first
        if "\"" in char or ("'" in char):
            if char_index != 0:
                # Pass over anything that is an escape character
                if line[char_index - 1] == "\\" or ("\'" in char and before_counter % 2 == 1 and "\"" in last_quotation):
                    continue
                else:
                    if char_index < index_to_check:
                        before_counter += 1
                        if before_counter % 2 == 1:
                            last_quotation = char
                        else:
                            last_quotation = ''
                    else:
                        after_counter += 1
            else:
                before_counter += 1

    # You are not in a string
    if before_counter % 2 == 0 :
        return False
    else:
        return True

# Draft of multi-line categorizer
def multiline_lines(lines, comment_lines):
    """
    Categorizes multiline things

    Used https://www.techbeamers.com/understand-python-statement-indentation/#how-to-use-multiline-statement
    as a guide to what type of multi-line exists

    :param lines:
    :return:
    """

    multi_line_stack = []
    multilines = []

    for line_number, line in enumerate(lines):

        # Checks to see if comment line
        if comment_lines[line_number]:
            multilines.append(0)
            continue
        if line_number == 158:
            print('blah')
            pass
        # stack algorithmn
        for char_index, char in enumerate(line):

            if char == "(":
                # Checks to see if the enclosure is not in a string
                if not check_if_in_string(line, char_index):
                    multi_line_stack.append('(')
            elif char == ")":
                # This check must occur after the above check as this is not ensured to work on quotations
                if not check_if_in_string(line, char_index):
                    multi_line_stack.pop()
            elif char == "{":
                if not check_if_in_string(line, char_index):
                    multi_line_stack.append('{')
            elif char == "}":
                if not check_if_in_string(line, char_index):
                    multi_line_stack.pop()
            elif char == "[":
                if not check_if_in_string(line, char_index):
                    multi_line_stack.append('[')
            elif char == "]":
                if not check_if_in_string(line, char_index):
                    multi_line_stack.pop()

        #  parenthesis or another closure makes this multi-lined
        if multi_line_stack:
            multilines.append(1)
            continue
        # Use the explicit multi-line character
        elif len(line.strip(" ").strip("\n")) > 0 and line.strip(" ").strip("\n")[-1] == "\\":
            multilines.append(1)
            continue

        # Default case if not multi-lined
        multilines.append(0)

    return multilines

def main():
    """
    Currently this function does some prescripted stuff.

    :return:
    """

    with open("./categorizer.py") as fp:
        # This scope is bothering me
        lines = fp.readlines()

    empty_lines = []
    assigment_lines = []
    conditional_lines = []
    control_lines = []
    indent_levels = []
    function_call_lines = []
    function_def_lines = []

    # Categorize and labels comment lines without code
    comment_lines = find_comment_lines(lines)
    # Gets rid of inlined comments
    strip_comments_after_code(lines, comment_lines)
    # Categorizes multi-lined systems
    multilines = multiline_lines(lines, comment_lines)

    # Categorizing lines
    for line_number, line in enumerate(lines):

        # Skip over if comment lines... we might need to rethink this, but it avoids problems in categorizing the rest..
        if comment_lines[line_number]:
            empty_lines.append(0)

            continue

        # Categorizing
        empty_lines.append(find_empty_lines(line))

    # Debug portion
    print("Mult-lined")
    print_all_cats(lines, multilines)

def print_all_cats(lines, category):
    """
    Debug printing

    :param lines:
    :param category:
    :return:
    """

    for line_number, line in enumerate(lines):

        print(str(line_number) + " " + str(category[line_number]) + " " + line.strip("\n"))


if __name__ == "__main__":
    main()