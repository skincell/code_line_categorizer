

def main():
    """
    Currently this function does some prescripted stuff.

    :return:
    """
    lines = []
    with open("./categorizer.py") as fp:
        lines = fp.readlines()



    # Debug portion
    empty_category = [0] * len(lines)
    print_all_cats(lines, empty_category)

def print_all_cats(lines, category):
    """
    Debug printing

    :param lines:
    :param category:
    :return:
    """

    for line_number, line in enumerate(lines):

        print(category[line_number] + " " + line)


if __name__ == "__main__":
    main()