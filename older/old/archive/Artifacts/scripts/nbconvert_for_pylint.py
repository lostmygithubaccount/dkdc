# This is similar to nbconvert to script.
# It converts a jupyter notebook specified by the first parameter
# into a python file specified by the second parameter.
# The difference with the regular nbconvert is that it ignores
# cells that start with %%writefile and removes the %%time line
# from the start of the cell if it exists.

# Also, the last line of a cell can be a variable name, which is printed by jupyter notebook.
# To avoid the pointless-statement warning in such cases, this script makes such lines a print of the variable.
# Note that check for identifier below implies that it is the last line of the cell
# because the identifier can't contain a "\n".
# So, we still get the pointless-statement warning for identifier lines that are not the last line, which is correct.
# This also allows identifier.identifier.

import json
import sys

notebook = json.load(open(sys.argv[1], 'r'))

with open(sys.argv[2], 'w') as outFile:
    for cell in notebook["cells"]:
        if cell['cell_type'] == 'code':
            source = cell['source']
            if not source[0].startswith('%%writefile'):
                if source[0] == '%%time\n':
                    del source[0]
                for line in source:
                    if not (line.startswith('%matplotlib') or line.startswith('!')):
                        if all(x.isidentifier() for x in line.split('.')):
                            outFile.write('print(' + line + ')')
                        else:
                            outFile.write(line)
                outFile.write('\n')
