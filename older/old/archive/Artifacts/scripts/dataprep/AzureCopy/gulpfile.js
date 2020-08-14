"use strict";
var argv = require('yargs').argv;
var gulp = require('gulp');
var gutil = require('gulp-util');
var merge2 = require('merge2');
var path = require('path');

var azure = require('./azureBlob');

var flavors = [ 'debug', 'ship' ];

// incantation:
// gulp upload --releaseDir "d:\Src\DPrep1\release\electron-win" --buildNr 0.1.1608.29011 --sasToken "?sv=2015-04-05&si=winbuilds-vso-upload&sr=c&sig=<...>" --container winbuilds
// in VSO release definition:
// gulp upload --releaseDir "$(System.DefaultWorkingDirectory)/DPrep Weekly (OSX)/ReleaseUnsigned" --storageAccount 6b62d0c15dfb5d58510e --sasToken "$(osxBuildsSasToken)" --container osxbuilds \
//             --buildNr $(Build.BuildNumber) --releaseType weekly-test
gulp.task("upload", function(done) {
  // path up to but NOT including the build flavor (debug, ship):
  let releaseDir = argv.releaseDir;
  // storage account name, without the .blob.core.windows.net part:
  let storageAccount = argv.storageAccount;
  // sasToken, i.e. query param of a SAS url (incl. the '?')
  let sasToken = argv.sasToken;
  // container name, winbuilds or osxbuilds
  let container = argv.container;
  // build nr, e.g. 0.1.1608.29011
  let buildNr = argv.buildNr;
  // release schedule type, e.g. 'daily', 'weekly', 'weekly-test'
  let releaseType = argv.releaseType || 'daily';

  if (!releaseDir) { fatal(done, 'releaseDir'); };
  if (!storageAccount) { fatal(done, 'storageAccount'); };
  if (!container) { fatal(done, 'container'); };
  if (!buildNr) { fatal(done, 'buildNr'); };
  if (!sasToken) { fatal(done, 'sasToken'); };

  let mergedStreams = merge2();
  let options = {
    host: `https://${storageAccount}.blob.core.windows.net/`,
    sasToken: sasToken,
    container: container,
    prefix: ''
  };
  let srcOptions = { base: releaseDir };

  flavors.forEach(function(flavor) {
    let droppedFiles = [
      `${releaseDir}${path.sep}${flavor}${path.sep}**`
    ];

    options.prefix = `${releaseType}/${buildNr}/${flavor}/`;
    mergedStreams.add(
      gulp.src(droppedFiles, srcOptions)
        .pipe(azure.upload(options)));

    options.prefix = `${releaseType}/latest/${flavor}/`;
    mergedStreams.add(
      gulp.src(droppedFiles, srcOptions)
        .pipe(azure.upload(options)));
  });

  return mergedStreams;
});

// incantation:
// gulp copyRelease --buildNr 0.1.1610.02012 --srcStorageAccount 6b62d0c15dfb5d58510e --srcAccessKey <...> --srcContainer osxbuilds --srcFlavor ship --srcReleaseType weekly-test
//                  --destStorageAccount pendletonpreview --destSasToken "?sv=2015-12-11&si=osx-vso-upload&sr=c&sig=<...>" --destContainer osx-ignore
gulp.task("copyRelease", function() {
  // build nr, e.g. 0.1.1608.29011
  let buildNr = argv.buildNr;
  // source storage account name from where to copy, without the .blob.core.windows.net part:
  let srcStorageAccount = argv.srcStorageAccount;
  // access key of source storage account:
  let srcAccessKey = argv.srcAccessKey;
  // source container name, winbuilds or osxbuilds
  let srcContainer = argv.srcContainer;
  // build flavor, e.g. 'debug', 'ship'
  let srcFlavor = argv.srcFlavor;
  // release schedule type, e.g. 'daily', 'weekly', 'weekly-test'
  let srcReleaseType = argv.srcReleaseType;
  // destination storage account name to where to copy, without the .blob.core.windows.net part
  // can be empty and will default to srcStorageAccount:
  let destStorageAccount = argv.destStorageAccount || srcStorageAccount;
  // destination sasToken for container, i.e. query param of a SAS url (incl. the '?')
  let destSasToken = argv.destSasToken;
  //  destination container name, windows or osx
  let destContainer = argv.destContainer;
  // build flavor, e.g. 'debug', 'ship'; can be null (e.g. for Preview builds)
  let destFlavor = argv.destFlavor;
  // destination release schedule type, e.g. 'weekly', 'weekly-test';
  // can be null (e.g for Preview builds where storage account name implies release type)
  let destReleaseType = argv.destReleaseType;

  if (!buildNr) { fatal(done, 'buildNr'); };
  if (!srcStorageAccount) { fatal(done, 'srcStorageAccount'); };
  if (!srcAccessKey) { fatal(done, 'srcAccessKey'); };
  if (!srcContainer) { fatal(done, 'srcContainer'); };
  if (!srcFlavor) { fatal(done, 'srcFlavor'); };
  if (!srcReleaseType) { fatal(done, 'srcReleaseType'); };
  if (!destStorageAccount) { fatal(done, 'destStorageAccount'); };
  if (!destSasToken) { fatal(done, 'destSasToken'); };
  if (!destContainer) { fatal(done, 'destContainer'); };

  let srcBlobPrefix = `${srcReleaseType}/${buildNr}/${srcFlavor}`;
  let destBlobPrefix = undefined;
  if (destReleaseType && destFlavor) {
    destBlobPrefix = `${destReleaseType}/${buildNr}/${destFlavor}`;
  }
  return azure
    .srcBlobs({
        host: srcStorageAccount,
        accessKey: srcAccessKey,
        container: srcContainer,
        blobPrefix: srcBlobPrefix,
        withSasToken: true })
    .pipe(azure.copyBlobs({
        host: `https://${destStorageAccount}.blob.core.windows.net/`,
        sasToken: destSasToken,
        container: destContainer,
        targetBlobPath: destBlobPrefix
      })
    );
});

function fatal(done, parameterName) {
  let msg = `Error: missing required parameter --${parameterName}`;
  gutil.colors.red(msg);
  done(Error(msg));
}

