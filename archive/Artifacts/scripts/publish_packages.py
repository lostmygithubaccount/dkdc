import os
import json
import glob

import az_utils as az


def upload_package(source, package, repo):
    for file in glob.glob(os.path.join(source, package.replace("-", "_") + "*.whl")):
        return az.blob_upload(
            container=repo["container"],
            file=file.replace('\\', '/'),
            name=repo["prefix"] + os.path.basename(file),
            accountname=repo["account"])
    return 1


def main(config, source, channel):

    if not config:
        raise Exception("Config is not specified")
    if not source:
        raise Exception("Source is not specified")

    with open(config, 'r') as f:
        cfg = json.loads(f.read())

    release = cfg["releases"][channel]

    packages_repo = cfg["targets"][release["package_repo"]]
    extensions_repo = cfg["targets"][release["extensions_repo"]]

    az.set_account(packages_repo["subscription"])

    results = {}
    for package, location in cfg["source"]["packages"].items():
        if package in release["packages"]:
            print("Uploading ", package)
            results[package] = upload_package(source, package, packages_repo)

    az.set_account(extensions_repo["subscription"])

    for extension, location in cfg["source"]["extensions"].items():
        if extension in release["extensions"]:
            print("Uploading ", extension)
            results[package] = upload_package(source, extension, extensions_repo)

    status = True
    for package, result in results.items():
        if result != 0:
            print("Package ", package, " not found")
            status = False
    if not status:
        raise Exception("Package upload failed")


if __name__ == '__main__':
    print("*******[Build packages]: START*******")
    import argparse

    parser = argparse.ArgumentParser(description='Run AzureML SDK build wheels')
    parser.add_argument('--config', default=None)
    parser.add_argument('--source', default=None)
    parser.add_argument('--channel', default="test")

    args = parser.parse_args()
    print(args)

    main(args.config, args.source, args.channel)

    print("*******[Build packages]: COMPLETE*******")
