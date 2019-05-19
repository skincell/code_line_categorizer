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
* hash lines and storage

# Todo List
* Modify hashing setup to present more useful data
* refactor to test hash functionality,
* refactor so the multiline and other passed in variables are less important/all over the place also
* command line calling and testing
--------------------------- After this then I start making the tool that will be used for establishing relationships for a single script.
* loops
* control statements -> break, continue, return, etc.
* indentation level
* a lot more

# Warnings List
* Don't Support scripts that have inlined docstrings on a code line. I am sure somebody does that, but if you want support on that type of coding style do it yourself...
* Also don't really support having " ''' " or " """ " strings outside of having a comment block. So if you use " ''' " in a conditional or anything else, I don't support it, and it might throw off all categorizations. Also in case you are assigning a variable a docstring which is possible, it will not work.
* Do not support python scripts that can not normally run.. for example the multi-line categorizer will not correctly understand that '({)}' is not valid code and will not work properly.

# Environment
This project was developed using Python 3.5.