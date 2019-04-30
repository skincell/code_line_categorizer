

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
    We treat comment lines as non-code or something that can
    cause false positives for other categorizers.

    Also comments + multi line is a double categorization.
    We are trying to keep categorizations mostly separate from each other,
    but this one breaks that rule.

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
        # Checking for multiline comment start or end
        elif ("\"\"\"" in line or "'''" in line) \
            and "if" not in line:
            # [ "if" not in line ^ ] is a hack that can come back to hurt me.


            comment_lines.append(1)

            # Closes or Opens a multi line comment block
            if multiline_comment:
                multiline_comment = False
            else:
                multiline_comment = True

            continue

        # Part of a multi line comment
        if multiline_comment:
            comment_lines.append(1)
            continue

        # If it hits nothing else then it appends a zero
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
        if comment_lines[line_number] == 1:
            continue

        # Try to find if a comment exists on code line
        try:
            comment_line_index = line.index("#")
        except ValueError:
            comment_line_index = None

        if comment_line_index != None:
            # inline comments should not appear when examining this using tools like the one below
            lines[line_number] = line[0:comment_line_index]  # Should disappear inline comments from the analyzer

def main():
    """
    Currently this function does some prescripted stuff.

    :return:
    """
    lines = []
    with open("./categorizer.py") as fp:
        lines = fp.readlines()

    empty_lines = []
    assigment_lines = []
    conditional_lines = []
    control_lines = []
    indent_levels = []
    function_call_lines = []
    function_def_lines = []

    # Categorize solely comment lines
    comment_lines = find_comment_lines(lines)
    # Sanatize the code from comments
    strip_comments_after_code(lines, comment_lines)
    # Get rid of comments on same lines as code


    # Categorizing lines
    for line in lines:
        empty_lines.append(find_empty_lines(line))

    # Debug portion
    print("Comment Lines")
    print_all_cats(lines, comment_lines)

def print_all_cats(lines, category):
    """
    Debug printing

    :param lines:
    :param category:
    :return:
    """

    for line_number, line in enumerate(lines):

        print(str(category[line_number]) + " " + line.strip("\n"))


if __name__ == "__main__":
    main()