import tempfile
import os
import json
import az_utils as az

blob_url_template = "https://{}.blob.core.windows.net/{}/{}"


def get_blobs(accountname, container, prefix):
    res = az.list_blobs(accountname=accountname,
                        container=container,
                        prefix=prefix)
    return json.loads(res)


def blob_url(accountname, container, name):
    return blob_url_template.format(accountname, container, name)


# TODO: generate token. ?: CDN link
def get_packages_structure(idx, repo, processed, generate_token=False):
    id = "|".join([repo["subscription"],
                   repo["account"],
                   repo["container"],
                   repo["prefix"]])
    if id in processed:
        print("Skipping: already processed")
        return
    processed.append(id)
    az.set_account(subscription=repo["subscription"])

    prlen = len(repo["prefix"])
    for blob in get_blobs(repo["account"], repo["container"], repo["prefix"]):
        if not blob["name"].endswith("whl"):
            continue
        deprefix = blob["name"][prlen:]
        part = deprefix.split("-", 2)
        url = blob_url(repo["account"], repo["container"], blob["name"])
        if repo["generatetoken"] == "true":
            url += "?" + az.generate_sas(
                accountname=repo["account"],
                container=repo["container"],
                name=blob["name"]).strip().strip('"')
        if part[0] not in idx.keys():
            idx[part[0]] = {
                part[1]: {
                    "url": url,
                    "name": deprefix}}
        else:
            idx[part[0]][part[1]] = {
                "url": url,
                "name": deprefix}


# ?: external support
def create_index(repo, idx, local_path, external=None):
    prefix = repo["prefix"]
    endpoint = repo["endpoint"]
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    with open(os.path.join(local_path, "index.html"), "w") as main:
        main.write("<html><head><title>Simple Index</title><meta name='api-version' value='2' /></head><body>")
        for package, items in idx.items():            normname = package.replace('.', '-').replace('_', '-')            main.write("<a href='https://{0}/{1}{2}'>{2}</a></br>".format(endpoint, prefix, normname))            packfolder = os.path.join(local_path, normname)            if not os.path.exists(packfolder):                os.makedirs(packfolder)            with open(os.path.join(packfolder, "index.html"), "w") as pack:                for i, info in items.items():                    pack.write("<a href='{0}' rel='external'>{1}</a><br/>".format(info["url"], info["name"]))        main.write("</body></html>")


def upload_index(repo, local_path):
    plen = len(local_path) + 1
    container = repo["container"]
    accountname = repo["account"]
    prefix = repo["prefix"]
    for root, dirs, files in os.walk(local_path):
        for file in files:
            if file == "index.html":
                az.blob_upload(container=container,
                               file=os.path.join(root, file).replace('\\', '/'),
                               name=os.path.join(prefix, root[plen:], file).replace('\\', '/'),
                               accountname=accountname)


def main(config, local_path, channel):

    if not config:
        raise Exception("Config is not specified")
    if not local_path:
        local_path = tempfile.TemporaryDirectory().name

    with open(config, 'r') as f:
        cfg = json.loads(f.read())

    release = cfg["releases"][channel]

    idxraw = {}
    processed = []
    get_packages_structure(idxraw, cfg["targets"][release["package_repo"]], processed)
    get_packages_structure(idxraw, cfg["targets"][release["extensions_repo"]], processed)

    create_index(cfg["targets"][release["index"]], idxraw, local_path)
    upload_index(cfg["targets"][release["index"]], local_path)


if __name__ == '__main__':
    print("*******[Update Index]: START*******")
    import argparse

    parser = argparse.ArgumentParser(description='Run AzureML SDK build wheels')
    parser.add_argument('--config', default=None)
    parser.add_argument('--local_path', default=None)
    parser.add_argument('--channel', default="test")

    args = parser.parse_args()
    print(args)

    main(args.config, args.local_path, args.channel)

    print("*******[Update Index]: COMPLETE*******")
