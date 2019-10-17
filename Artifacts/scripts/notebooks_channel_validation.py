import os
import json
from argparse import ArgumentParser


def validate(file, test, release):
    with open(file) as f:
        content = json.loads(f.read())
    if not all(x in content["channels"].get(test, []) for x in content["channels"].get(release, [])):
        raise Exception("{}: notebooks in {} channel must be in {}".format(file, release, test))


def walkthedir(path, test, release):
    for root, dirs, files in os.walk(path):
        for f in files:
            fullpath = os.path.join(root, f)
            if os.path.basename(fullpath) == "release.json":
                validate(fullpath, test, release)


parser = ArgumentParser()
parser.add_argument("--path", dest="path", type=str, default=".")
parser.add_argument("--test", dest="test", type=str, default="master")
parser.add_argument("--release", dest="release", type=str, default="preview")
args = parser.parse_args()
walkthedir(args.path, args.test, args.release)
