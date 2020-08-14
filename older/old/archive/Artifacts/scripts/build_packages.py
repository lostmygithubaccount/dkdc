import json
import os
import sys
import shutil
from utils import run_command


def build_package(path, name, destination, python):
    curpath = os.getcwd()
    os.chdir(path)
    shutil.rmtree("build", True)
    shutil.rmtree(name + ".egg-info", True)
    shutil.rmtree("dist", True)
    ret_code = run_command([python, "setup.py", "bdist_wheel"], throw_on_retcode=False)
    print("### Process returned code ", ret_code)
    os.chdir(curpath)
    for root, dirs, files in os.walk(os.path.join(path, "dist")):
        for file in files:
            if file.endswith(".whl"):
                print("### Copying wheel into ", destination)
                shutil.copy(os.path.join(root, file), destination)
    return ret_code


def main(config, source, destination, channel, python):

    if not config:
        raise Exception("Config is not specified")
    if not source:
        raise Exception("Source is not specified")
    if not source:
        raise Exception("Destination is not specified")

    with open(config, 'r') as f:
        cfg = json.loads(f.read())

    release = cfg["releases"][channel]

    results = {}
    for package, location in cfg["source"]["packages"].items():
        if package in release["packages"]:
            print("Building ", package, " from location ", location)
            results[package] = build_package(os.path.join(source, location), package, destination, python)

    for extension, location in cfg["source"]["extensions"].items():
        if extension in release["extensions"]:
            results[package] = build_package(os.path.join(source, location), extension, destination, python)

    status = True
    for package, result in results.items():
        if result != 0:
            print("Package ", package, " build failed")
            status = False
    if not status:
        raise Exception("Package build failed")


if __name__ == '__main__':
    print("*******[Build packages]: START*******")
    import argparse

    parser = argparse.ArgumentParser(description='Run AzureML SDK build wheels')
    parser.add_argument('--config', default=None)
    parser.add_argument('--source', default=None)
    parser.add_argument('--destination', default=None)
    parser.add_argument('--channel', default="test")
    parser.add_argument('--python', default=sys.executable)

    args = parser.parse_args()
    print(args)

    main(args.config, args.source, args.destination, args.channel, args.python)

    print("*******[Build packages]: COMPLETE*******")
