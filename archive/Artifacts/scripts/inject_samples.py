import os
import json
import sys

if sys.version_info >= (3, 0):
    from urllib.request import Request, urlopen

identifier = ".. code-block:: inject"
codeblock = ".. code-block:: python"
linesep = '\n'
rootpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')


def check_url(url):
    try:
        return urlopen(Request(url, method="GET")).getcode() == 200
    except:
        return False


def get_all_py_files(path):
    pyfiles = []
    for root, dirs, files in os.walk(path):
        pyfiles.extend([os.path.join(root, file) for file in files if file.endswith(".py")])
    return pyfiles


def get_code_sample_notebook(indentation, file, sampletag):
    with open(file) as f:
        notebook = json.loads(f.read())
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            metadata = cell.get("metadata")
            if metadata:
                tags = metadata.get("tags")
                if tags and sampletag in tags:
                    return [' ' * indentation + line for line in cell["source"]]
    raise Exception("Unable to locate sample in {}".format(file))


def get_code_sample_script(indentation, file, sampletag):
    tag = "# " + sampletag
    tagbegin = tag + ":begin"
    tagend = tag + ":end"
    with open(file) as f:
        content = f.readlines()
    start = ([line.lstrip().startswith(tagbegin) for line in content]).index(True)
    end = ([line.lstrip().startswith(tagend) for line in content]).index(True)
    sample = content[start + 1:end]
    sampleindent = len(content[start]) - len(content[start].lstrip())
    diff = sampleindent - indentation
    if diff >= 0:
        return [line[diff:] for line in sample]
    else:
        return [(' ' * (- diff) + line) for line in sample]


def get_code_sample(instructions, indent):
    print(instructions)
    instructions = (instructions[len(identifier):]).strip()
    indentation = indent + 4
    parts = instructions.split('#')
    srcfile = parts[0].lstrip('/').lstrip('\\')
    print(srcfile)
    file = os.path.join(rootpath, srcfile)

    print(file)
    if not os.path.isfile(file):
        raise Exception("{} does not exist".format(file))

    alignedsample = [(' ' * indent) + codeblock + linesep, linesep]
    if file.endswith(".py"):
        alignedsample.extend(get_code_sample_script(indentation=indentation, file=file, sampletag=parts[1]))
    elif file.endswith(".ipynb"):
        alignedsample.extend(get_code_sample_notebook(indentation=indentation, file=file, sampletag=parts[1]))
    else:
        raise Exception("Unknown sample source file format")

    # remove empty lines
    for i in range(len(alignedsample)):
        if not alignedsample[i].strip():
            alignedsample[i] = linesep
        else:
            alignedsample[i] = alignedsample[i].rstrip() + linesep

    if srcfile.startswith("notebooks/"):
        url = "https://github.com/Azure/MachineLearningNotebooks/blob/master/" + srcfile.lstrip("notebooks/")
        print(url)
        if check_url(url):
            alignedsample.append(linesep)
            alignedsample.append(' ' * indent + "Full sample is available from" + linesep)
            alignedsample.append(' ' * indent + url + linesep)
            alignedsample.append(linesep)

    # print("".join(alignedsample))
    return alignedsample


def inject_samples(path, vsoonly=True):
    if sys.version_info < (3, 0):
        print("Skipping samples injection for py2")
        return
    if os.environ.get("BUILD_DEFINITIONNAME") or not vsoonly:
        for file in get_all_py_files(path):
            with open(file, encoding='utf8') as f:
                content = f.readlines()
            newcontent = []
            hascodeblocks = False
            i = 0
            while i < len(content):
                line = content[i]
                trimmedline = line.strip()
                if trimmedline.startswith(identifier):
                    indent = len(line) - len(trimmedline) - 1
                    hascodeblocks = True
                    while content[i + 1].strip():
                        trimmedline += content[i + 1].strip()
                        i += 1

                    sample = get_code_sample(trimmedline, indent)
                    newcontent.extend(sample)
                else:
                    newcontent.append(line)
                i += 1
            if hascodeblocks:
                with open(file, "w+") as f:
                    f.writelines(newcontent)
