""" Create and update a PyPi simple repo index.
Enumerates wheels found in an Azure blob location
then generates index html files and uploads to a separate blob location
to form a simple PyPI repo.
Simple repo structure, see: https://www.python.org/dev/peps/pep-0503/
"""

import json
import os
import re
import sys
import tempfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlparse

# a recent update of az CLI hides the current directory from the import path:
sys.path.append(os.path.realpath(os.curdir))
from azureBlob import AzureBlob


def createIndex(wheels, baseUrl):
    index = defaultdict(dict)
    for wheel in wheels:
        pkgName, wheelName = getPackageName(wheel)
        index[pkgName][wheelName] = urljoin(baseUrl, wheel)
    return index


def getPackageName(fullName):
    # fullName is a URL part, always parse for '/'
    wheelName = PurePosixPath(fullName).name
    pkgName, *_ = wheelName.split('-')
    return (re.sub(r'[_.]+', '-', pkgName.lower()), wheelName)


def generateHtml(name, wheels, updated, version):
    return '<!DOCTYPE html><html><head><title>{0}</title></head><body>\n'.format(name) \
        + '<h1>{0}</h1>\n'.format(name) \
        + '\n'.join(['<a href="{1}">{0}</a><br/>'.format(name, url) for (name, url) in sorted(wheels.items())]) \
        + '\n<p>Updated: {0} {1}</p>'.format(updated, '(build ' + version + ')' if version else '') \
        + '\n</body></html>'


def generateHtmlList(index, topProjectName, version):
    # PEP503 requires the hrefs to project pages to end in a trailing '/'
    # the Azure CDN url rewrite rule also uses that to append a 'index.html' to such request urls
    # source match: ((?:[^\?]*/)?)($|\?.*) => destination: $1index.html$2
    # regex details: https://regex101.com/r/cuf2OM/1
    projects = {p: p + '/' for p in index.keys()}
    updated = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    yield 'index.html', generateHtml(topProjectName, projects, updated, version)

    for name, entry in index.items():
        yield name + '/index.html', generateHtml(name, entry, updated, version)


def writeHtml(htmlList, tmpDir):
    log("generating html files for simple index:")
    for name, htmlContent in htmlList:
        fullPath = os.path.join(tmpDir, name)
        log('>> {0}...', name)
        Path(os.path.dirname(fullPath)).mkdir(parents=True, exist_ok=True)
        with open(fullPath, 'w', encoding='utf-8') as fp:
            fp.write(htmlContent)


def log(msg, *args):
    msg += '\n'
    sys.stdout.write(msg.format(*args))

def formatPath(path, version):
    if not version:
        return path
    return path.format(version=version) if '{' in path and '}' in path else path

def main(config, enumerateRecursively, version):
    log('az CLI installation info:\n{0}', AzureBlob.version())
    loggedIn, msg = AzureBlob.isLoggedIn()
    if not loggedIn:
        log(msg)
        sys.exit(1)
    wheelsRepo = formatPath(config['wheelsRepo'], version)
    azDrop = AzureBlob(wheelsRepo, config['subscription'])
    log('enumerating wheels in {0}...', wheelsRepo)
    blobs = azDrop.listBlobs(enumerateRecursively)
    wheels = [blob for blob in blobs if PurePosixPath(blob).suffix == '.whl']
    wheelCnt = len(wheels)
    log('found {0} wheels.', wheelCnt)
    if (wheelCnt == 0):
        log('No wheels discovered, aborting.')
        sys.exit(1)
    index = createIndex(wheels, config['cdnBaseUrl'])
    htmlList = generateHtmlList(index, azDrop.container, version)

    uploadTarget = formatPath(config['uploadTarget'], version)
    azPyPi = AzureBlob(uploadTarget, config['subscription'])
    with tempfile.TemporaryDirectory() as tmpDir:
        writeHtml(htmlList, tmpDir)
        log('uploading generated index to {0}...', uploadTarget)
        azPyPi.uploadBlobs(tmpDir, 'text/html')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Update a simple PyPi compatible repo index; enumerate wheels in blob storage'
    )
    parser.add_argument(
        '-c', '--config',
        default=None,
        required=True,
        help=
        'config file with a JSON object with these members: subscription, wheelsRepo (url to Azure blob drop location), cdnBaseUrl (base url of CDN fronting blob), uploadTarget (url of Azure blob to upload index to'
    )
    parser.add_argument(
        '--version', default=None, help='repo build version from build system')
    parser.add_argument('-r', '--recursive', action='store_true', help='enumerate wheelsRepo recursively')
    parser.add_argument(
        '--wheelsRepo',
        default=None,
        help='if set, overrides value from config JSON')
    parser.add_argument(
        '--uploadTarget',
        default=None,
        help='if set, overrides value from config JSON')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as configFile:
        config = json.load(configFile)
    if args.wheelsRepo: config['wheelsRepo'] = args.wheelsRepo
    if args.uploadTarget: config['uploadTarget'] = args.uploadTarget
    main(config, args.recursive, args.version)
