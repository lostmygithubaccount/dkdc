import json
import os
import sys
import subprocess
import time
from pathlib import PurePosixPath
from urllib.parse import urlparse

class AzureBlob:
    """ AzureBlob supports blob manipulations needed in the context of wheels indexing and releasing.
    Uses az CLI v2 for the actual Azure blob access.

    Code assumes that the calling user is already logged in via 'az login';
    this is already the case when using this script as a VSTS "Azure CLI" task
    """

    def __init__(self, blobPath, subscription=None):
        self.account, self.container, self.prefix = self._parse(blobPath)
        self.blobArgs = ['--account-name', self.account]
        if subscription:
            self._runCmd(['az', 'account', 'set', '-s', subscription])

    """ isLoggedIn tests if current used is logged in to az CLU; returns true if logged in.
    """
    @staticmethod
    def isLoggedIn():
        acctList, warning = AzureBlob._runCmd(['az', 'account', 'list'])
        accounts = json.loads(acctList)
        if len(accounts) == 0 and warning != '':
            return False, warning
        else:
            return True, ''

    """ version returns a string with version info of az CLI and its command handlers.
    """
    @staticmethod
    def version():
        data, warning = AzureBlob._runCmd(['az', '--version'])
        return data

    """ listBlobs enumerates blobs and returns a generator list of blobs encountered.
    """
    def listBlobs(self, enumerateRecursively):
        listCmd = ['--container-name', self.container]
        if self.prefix:
            listCmd += ['--prefix', self.prefix]
        listCmd += ['--query', '[].name']
        jsonList, _ = self._runAz('list', *listCmd)
        wheels = json.loads(jsonList)
        return self._filterSameFolderBlobs(wheels, self.prefix, enumerateRecursively)

    """ uploadBlobs does a batch upload of blobs found in the srcFolder.
    """
    def uploadBlobs(self, srcFolder, contentType='application/octet-stream'):
        self._runAz('upload-batch', '--source', srcFolder, '--destination', self.container, '--destination-path', self.prefix, \
            '--content-type', contentType, '--content-cache-control', 'max-age=3600, must-revalidate')

    """ copyBlobsFrom copies blobs from sourceUrl to this instance's container and prefix.
    Returns a dictionary of blob: copyStatus
    """
    def copyBlobsFrom(self, sourceUrl):
        srcAcct, srcContainer, srcPrefix = self._parse(sourceUrl)
        srcBlobs = AzureBlob(sourceUrl).listBlobs(enumerateRecursively=True)
        pendingCopyBlobs = {file: self._startCopy(srcAcct, srcContainer, file, self._removeCommonPath(file, srcPrefix)) for file in srcBlobs}

        completedBlobs = {}
        while True:
            pendingCopyBlobs = dict(self._filterPendingBlobCopy(pendingCopyBlobs, completedBlobs))
            if len(pendingCopyBlobs) == 0:
                break
            time.sleep(20)
        return completedBlobs

    def _parse(self, blobUrl):
        url = urlparse(blobUrl)
        account, *_ = url.netloc.split('.')
        _, container, *rest = url.path.split('/')
        prefix = '/'.join(rest)
        return account, container, prefix

    def _filterSameFolderBlobs(self, seq, prefix, allowNestedFolders):
        for file in seq:
            # use posix style parsing for URL paths, this will correctly parse urls on windows
            path = PurePosixPath(file)
            relPath = path.relative_to(prefix)
            if allowNestedFolders or relPath.parent.name == '':
                yield file

    def _removeCommonPath(self, path, commonPrefix):
        return str(PurePosixPath(path).relative_to(commonPrefix))

    def _startCopy(self, srcAccount, srcContainer, srcBlob, destBlob):
        # copy start-batch would be the preferred choice but it doesn't allow to shorten the destination paths
        # using start-batch results in part of the paths to be duplicated on the destination side
        result, _ = self._runAz('copy', 'start',
                             '--source-account-name', srcAccount,
                             '--source-container', srcContainer,
                             '--source-blob', srcBlob,
                             '--destination-container', self.container,
                             '--destination-blob', self.prefix + '/' + destBlob)
        return json.loads(result)

    def _filterPendingBlobCopy(self, blobsDict, completedBlobs):
        for blob, result in blobsDict.items():
            if result['status'] == 'success':
                completedBlobs[blob] = result
                continue
            copyJson, _ = self._runAz('show', '--container-name', self.container, '--name', blob, '--query', 'properties.copy')
            copyState = json.loads(copyJson)
            if copyState['status'] in ('success', 'failed'):
                completedBlobs[blob] = copyState
            else:
                yield blob, copyState

    def _runAz(self, verb, *argv):
        cmd = ['az', 'storage', 'blob', verb]
        cmd += argv
        cmd += self.blobArgs
        return self._runCmd(cmd)

    @staticmethod
    def _runCmd(cmd):
        useShell = False if os.name == 'posix' else True
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=useShell) as proc:
            out, err = proc.communicate()
            errStr = err.decode() if err else '<None>'
            if proc.returncode != 0:
                raise Exception(
                    'WheelsAzureBlob exit code: {0}, error: {1}'.format(proc.returncode, errStr))
            return out.decode(), errStr
