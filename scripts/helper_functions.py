

def check_if_in_string(line, index_to_check):
    # TODO we use and will be using this function a lot; see if there is a way to reduce runtime in function.
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
