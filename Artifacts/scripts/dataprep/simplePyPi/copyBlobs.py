""" Copy blobs within same storage account.
"""
import json
import sys
import os

# a recent update of az CLI hides the current directory from the import path:
sys.path.append(os.path.realpath(os.curdir))
from azureBlob import AzureBlob

def log(msg, *args):
    msg += '\n'
    sys.stdout.write(msg.format(*args))


def main(sourceUrl, destinationUrl):
    loggedIn, msg = AzureBlob.isLoggedIn()
    if not loggedIn:
        log(msg)
        sys.exit(1)
    azDrop = AzureBlob(destinationUrl)
    log('Copying from {0}', sourceUrl)
    log('          to {0}...', destinationUrl)
    blobs = azDrop.copyBlobsFrom(sourceUrl)
    errors = 0
    for blob, copyState in blobs.items():
        log('>> {0}: {1}', blob, copyState['status'])
        if (copyState['status'] != 'success'):
            log('   error detail: {0}]', copyState['statusDescription'])
            errors += 1
    if errors > 0:
        sys.exit(2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description= 'Copy blobs recursively from source to target blob URL.')
    parser.add_argument('-s', '--sourceUrl', default=None, required=True, help='source url to blob to copy from')
    parser.add_argument('-d', '--destinationUrl', default=None, required=True, help='source url to blob to copy to')
    args = parser.parse_args()

    main(args.sourceUrl, args.destinationUrl)
