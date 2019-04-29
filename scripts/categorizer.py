

def find_empty_lines(line):
    """
    Returns 1 for an empty line and 0 for non-empty
    :param line:
    :return:
    """
    if line.strip("\t").strip(" ").strip("\n") == '':
        return 1

    return 0



def main():
    """
    Currently this function does some prescripted stuff.

    :return:
    """
    lines = []
    with open("./categorizer.py") as fp:
        lines = fp.readlines()

    empty_lines = []
    comment_lines = []
    assigment_lines = []
    conditional_lines = []
    control_lines = []
    indent_levels = []
    function_call_lines = []
    function_def_lines = []

    # Categorizing lines
    for line in lines:
        empty_lines.append(find_empty_lines(line))


    # Debug portion
    print("Empty Lines")
    print_all_cats(lines, empty_lines)

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