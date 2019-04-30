# Plans
This code base is meant to categorize each line of a *python* script several different ways. Currently only python is planned for this tool.

Current Categoires:
* comments
* empty lines

Next to be supported
* multi-line

Don't Support scripts that have inlined docstrings on a code line.
I am sure somebody does that, but if you want support on that type of coding style do it yourself...

Also don't really support having "'''" or "\"\"\"" strings outside of having a comment block.
So if you use "'''" in a conditional or anything else, I don't support it, and it might throw off all categorizations.