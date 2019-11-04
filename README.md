# Plans
This code base is meant to categorize each line of a *python* script several different ways. Currently only python is planned for this tool.

# Current Categoires
* comments
* empty lines
* multi-line
* conditionals
* function defs
* assignments
* function calls
* indentation levels / scope levels?

# Additional functionality
* hash lines and storage
* command line calling
* finding matching function calls and defs
*


# Todo List
--------------------------- After this then I start making the tool that will be used for establishing relationships for a single script.
* stich together the usage of the variables and highlight the usage lines.
* loops
* control statements -> break, continue, return, etc.
* Dealt with different assignments by making sub categories for each one rather than one broad category.... Revisit this.
* Add integration testing
* a lot more

# Warnings List
* Don't Support scripts that have inlined docstrings on a code line. I am sure somebody does that, but if you want support on that type of coding style do it yourself...
* Also don't really support having " ''' " or " """ " strings outside of having a comment block. So if you use " ''' " in a conditional or anything else, I don't support it, and it might throw off all categorizations. Also in case you are assigning a variable a docstring which is possible, it will not work.
* Do not support python scripts that can not normally run.. for example the multi-line categorizer will not correctly understand that '({)}' is not valid code and will not work properly.

# Environment
This project was developed using Python 3.5.