

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

        # Try to find if a comment exists on code line
        try:
            comment_line_index = line.index("#")
        except ValueError:
            comment_line_index = None

        if comment_line_index != None:

            # Trying to capture the excpetion that a # in is in a string rather than after code on a line
            string_quotes = []

            # Tries to find the indices of enclosing quotations
            for char_index, char in enumerate(line):

                # 0 index if, check previous if escape then ignore, check if \" or '
                if "\"" in char or "'" in char:
                    if char_index != 0:
                        # Pass over anything that is an escape character
                        if line[char_index - 1] == "\\":
                            continue
                        else:
                            string_quotes.append(char_index)
                    else:
                        string_quotes.append(char_index)

            # Make sure that there are matching amount of quotations -> possible exceptionn multiline
            if len(string_quotes) % 2 != 0:
                # TODO update to actual name of script
                raise RuntimeError("line %s: The string quotes are not seeming to create enclosing quotations" % (line_number))

            for index in range(int(len(string_quotes) / 2)):
                if string_quotes[2 * index] < comment_line_index and comment_line_index < string_quotes[2 * index + 1]:


            else:
                # inline comments should not appear when examining this using tools like the one below
                lines[line_number] = line[0:comment_line_index]  # Should disappear inline comments from the analyzer


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

        # stack algorithmn
        for char in line:
            if char == "(":
                multi_line_stack.append('(')
            elif char == ")":
                multi_line_stack.pop()
            elif char == "{":
                multi_line_stack.append('{')
            elif char == "}":
                multi_line_stack.pop()
            elif char == "[":
                multi_line_stack.append('[')
            elif char == "]":
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