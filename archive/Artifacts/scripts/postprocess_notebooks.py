# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import json
from shutil import copyfile, rmtree
from argparse import ArgumentParser
from build_nb_index import index_post_process


DO_NOT_DELETE = ["Dockerfiles", ".gitignore", ".git"]


def copy_files(src, dst):
    src = os.path.normpath(src)
    dst = os.path.normpath(dst)
    if os.path.isdir(src):
        for item in os.listdir(src):
            copy_files(os.path.join(src, item), os.path.join(dst, item))
    else:
        dir = os.path.dirname(dst)
        if not os.path.exists(dir):
            os.makedirs(dir)
        copyfile(src, dst)


# NOTEBOOK COPYING FUNCTIONS
# Copy notebooks within single folder, and their dependencies
def copynb(release, source_folder, dest_folder):
    # Merge list of notebooks from different channels
    nblist = []
    for channel in channels:
        if channel in release["channels"]:
            nblist += release["channels"][channel]

    # Iterate over notebook list
    for elem in nblist:
        this_nb = release["notebooks"][elem]
        name = this_nb["name"]
        try:
            path = this_nb["path"]
        except Exception:
            path = "."

        # Create folder for notebook and copy it
        infolder = os.path.join(source_folder, path)
        outfolder = os.path.join(dest_folder, path)
        ymlfile = name.replace(".ipynb", ".yml")
        copy_files(os.path.join(infolder, name), os.path.join(outfolder, name))
        if os.path.exists(os.path.join(infolder, ymlfile)):
            copy_files(os.path.join(infolder, ymlfile), os.path.join(outfolder, ymlfile))

        # Copy dependencies
        if "dependencies" in this_nb:
            for dep in this_nb["dependencies"]:
                outdep = os.path.normpath(os.path.join(outfolder, dep))
                indep = os.path.normpath(os.path.join(infolder, dep))
                copy_files(indep, outdep)


# Recursive copy of notebook folders given release.json
def subcopy(source, destination):
    # Read release.json
    with open(os.path.join(source, "release.json"), "r") as fin:
        release = json.load(fin)

    # Check if anything needs publishing and publish them
    is_public = [
        ch in release["channels"] and len(release["channels"][ch]) > 0
        for ch in channels]

    if any(is_public):
        copynb(release, source, destination)

    # Recursive iteration to any include folders
    if "include" in release:
        for subkey, subfolder in release["include"].items():
            sub_source = os.path.join(source, subfolder)
            sub_dest = os.path.join(destination, subfolder)
            subcopy(sub_source, sub_dest)

    # Copy uploads
    if "uploads" in release:
        for elem in release["uploads"]:
            upload_source = os.path.join(source, elem)
            upload_destination = os.path.join(destination, elem)
            copy_files(upload_source, upload_destination)

    # Copy any README.md files
    if any(is_public):
        mds = [elem for elem in os.listdir(source) if elem == "README.md"]
        for elem in mds:
            copy_files(os.path.join(source, elem), os.path.join(destination, elem))


# NOTEBOOK POST-PROCESSING FUNCTIONS
# Little utility method to remove specific first character
def remove_first(s, r):
    if s[0] == r:
        return s[1:]
    return s


# Little utility to check if cell has code
def has_code(cell):
    return cell["cell_type"] == "code" and len(cell["source"]) > 0


# Strip #TESTONLY cells
def test_cell(cell):
    return has_code(cell) and "#TESTONLY" in cell["source"][0]


# Strip comments from #PUBLISHONLY cells
def publish_cell(cell):
    if has_code(cell) and "#PUBLISHONLY" in cell["source"][0]:
        cell["source"].pop(0)
        cell["source"] = [remove_first(row, "#") for row in cell["source"]]
    return cell


# Replace AZUREML-SDK-VERSION with specified version
def sdk_version(cell, sdk_ver):
    if cell["cell_type"] == "code":
        cell["source"] = [
            elem.replace("AZUREML-SDK-VERSION", sdk_ver)
            for elem in cell["source"]]
    return cell


# Post-processing walk over notebook folder
def post_process(notebooks_dir, sdk_ver):
    for r, d, files in os.walk(notebooks_dir):
        for f in files:
            # Handle only notebooks
            if not f.endswith(".ipynb") or f.endswith('checkpoint.ipynb'):
                continue

            file_path = os.path.join(r, f)
            with open(file_path, 'r') as fin:
                content = json.load(fin)

            # Post-process cell content
            content["cells"] = [
                sdk_version(publish_cell(cell), sdk_ver)
                for cell in content["cells"] if not test_cell(cell)]

            # Set new kernel names
            content['metadata']['kernelspec']['display_name'] = 'Python 3.6'
            content['metadata']['kernelspec']['name'] = 'python36'

            # Print out processed notebooks plus authors
            print(f, content['metadata']['authors'][0]["name"])
            with open(file_path, 'w') as fout:
                json.dump(content, fout, indent=2)


def clean_repo(dest):
    for item in os.listdir(dest):
        if item not in DO_NOT_DELETE:
            if os.path.isdir(item):
                rmtree(item)
            else:
                os.remove(item)

# USAGE:
# python preprocess_notebooks.py
# --sdk-version 1.2.3
# --source srcrepo
# --destination destrepo
# --channels preview databricks-preview preview-notest


channels = ["preview", "databricks-preview", "preview-notest"]
parser = ArgumentParser()
parser.add_argument("--sdk-version", dest="ver", type=str, default="")
parser.add_argument("--source", dest="src", type=str, default=".")
parser.add_argument("--destination", dest="dest", type=str, default=".")
parser.add_argument("--cleanrepo", dest="clean", type=bool, default=True)
parser.add_argument(
    "--channels", dest="channels", nargs="+", type=str, default=channels)
args = parser.parse_args()
channels = args.channels

if args.clean:
    clean_repo(args.dest)

subcopy(args.src, args.dest)
post_process(args.dest, args.ver)
index_post_process(args.dest)
