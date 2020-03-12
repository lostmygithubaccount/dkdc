"use strict";
var azure = require('azure-storage');
var es = require('event-stream');
var gutil = require('gulp-util');
var mime = require('mime');
var path = require('path');
var queue = require('queue');
var createReadStream = require('streamifier').createReadStream;
var through2 = require('through2');
var vfs = require('vinyl-fs');
var Vinyl = require('vinyl');
var url = require('url');

module.exports.upload = function (opts) {
  if (!opts.host) {
    throw new Error('Missing host option.');
  }
  if (!opts.sasToken) {
    throw new Error('Missing sasToken option.');
  }
  if (!opts.container) {
    throw new Error('Missing container option.');
  }

  var prefix = opts.prefix || '';
  var service = azure.createBlobServiceWithSas(opts.host, opts.sasToken).withFilter(new azure.LinearRetryPolicyFilter());
  var q = queue({ concurrency: 4, timeout: 1000 * 60 * 2 });
  var count = 0;
  var stream = es.through(function(file) {
    var that = this;

    if (file.isDirectory()) {
      return;
    }

    q.push(function(done) {
      let istream = file.isBuffer() ? createReadStream(file.contents) : file.contents;
      let filePath = prefix + file.basename;
      gutil.log(`queueing file for upload: ${file.path} to: ${opts.host}${opts.container}/${filePath}`);
      let ostream = service.createWriteStreamToBlockBlob(
        opts.container,
        filePath,
        { metadata: { fsmode: file.stat.mode }, contentType: mime.lookup(file.relative) },
        function(err) {
          if (err) { throw new Error(`Cannot create writeStreamToBlob: ${err.message}`); }

          that.push(file);
          done();
        }
      );

      istream.pipe(ostream);
    });
  }, function () {
    var that = this;
    q.on('success', function () {
      count++;
    });
    q.on('error', function (err) { that.emit('error', err); });
    q.start(function () {
      gutil.log(`${count} files uploaded to ${opts.container}/${prefix}.`);
      that.emit('end');
    });
  }
 );

  return stream;
};

module.exports.srcBlobs = function (srcOpts) {
  if (!srcOpts.host) {
    throw new Error('Missing source host option.');
  }
  if (!srcOpts.accessKey) {
    throw new Error('Missing source access key option.');
  }
  if (!srcOpts.container) {
    throw new Error('Missing source container option.');
  }
  let withSasToken = srcOpts.withSasToken || false;

  let service = azure.createBlobService(srcOpts.host, srcOpts.accessKey).withFilter(new azure.LinearRetryPolicyFilter());

  let stream = through2.obj();

  service.listBlobsSegmentedWithPrefix(srcOpts.container, srcOpts.blobPrefix, null, function(error, result, response) {
    if (error) {
      throw new Error(`Cannot list blobs: ${error}`);
    }
    let sasPolicy = _getReadSasPolicy(60);
    let hostParts = url.parse(service.host.primaryHost);
    result.entries.map(function(blob) {
      let token = service.generateSharedAccessSignature(srcOpts.container, blob.name, sasPolicy);
      let basename = path.basename(blob.name);
      let urlFormat = {
        protocol: hostParts.protocol,
        hostname: hostParts.hostname,
        pathname: `${srcOpts.container}/${blob.name}`
      };
      if (withSasToken) {
        urlFormat.search = token;
      }
      return { url: url.format(urlFormat), baseBlobName: basename };
    })
    .forEach(function(item){
      let vinyl = new Vinyl({ path: item.url });
      vinyl.url = item.url;
      vinyl.baseBlobName = item.baseBlobName;
      stream.push(vinyl);
    });
    // signal end of source stream
    stream.push(null);
  });
  return stream;
};

module.exports.copyBlobs = function (destOpts) {
  if (!destOpts.host) {
    throw new Error('Missing destination host option.');
  }
  if (!destOpts.sasToken) {
    throw new Error('Missing destination sasToken option.');
  }
  if (!destOpts.container) {
    throw new Error('Missing destination container option.');
  }

  let service = azure.createBlobServiceWithSas(destOpts.host, destOpts.sasToken).withFilter(new azure.LinearRetryPolicyFilter());
  let stream = through2.obj(function(file, encoding, done) {
    var that = this;
    // ensure file points to a azure blob, sourced from srcBlobs() method above
    if (!file.url) {
      return;
    }
    let container = destOpts.container;
    let targetBlob = destOpts.targetBlobPath ? `${destOpts.targetBlobPath}/${file.baseBlobName}` : `${file.baseBlobName}`;
    gutil.log(`Copying blob ${file.baseBlobName} to ${destOpts.host}${container}/${targetBlob}...`);
    service.startCopyBlob(file.url, container, targetBlob, function(error, result, response) {
      if (error) {
        throw new Error(`Cannot copy blobs: ${error}`);
      }
      let copyId = result.copy.id;
      let pollForCopyCompletion = setInterval(function () {
        service.getBlobProperties(container, targetBlob, function(error, properties) {
          if (error) {
            throw new Error(`Cannot get blob properties: ${error}`);
          }
          gutil.log(`  progress: ${destOpts.host}${container}/${targetBlob}: ${properties.copy.progress}, (${properties.copy.status})`);
          if (properties.copy.status !== 'pending') {
            clearInterval(pollForCopyCompletion);
            if (properties.copy.status === 'success') {
              gutil.log(`Copy to ${destOpts.host}${container}/${targetBlob} completed.`);
              that.push(file);
              done();
            } else {
              done(new Error('Error copying blob: ' + file.baseBlobName + ': ' + properties.copy.statusDescription));
            }
          }
        });
      }, 5 * 1000);
    });
  });
  return stream;
};

function _getReadSasPolicy(durationMinutes)
{
  var startDate = new Date();
  var expiryDate = new Date();
  expiryDate.setMinutes(startDate.getMinutes() + durationMinutes);
  startDate.setMinutes(startDate.getMinutes() - 5);

  return {
    AccessPolicy: {
      Permissions: azure.BlobUtilities.SharedAccessPermissions.READ,
      Start: startDate,
      Expiry: expiryDate
    },
  };
}
