"use strict";
const fs = require('fs');
const path = require('path');
class EmbeddedLicenseFileScanner {
    getLicense(module) {
        return EmbeddedLicenseFileScanner.LicenseFiles.reduce((licenseRetrieved, fileToCheck) => {
            if (licenseRetrieved) {
                return licenseRetrieved;
            }
            try {
                let licensePath = path.join(module.path, fileToCheck);
                return fs.readFileSync(licensePath, { encoding: 'utf8' });
            }
            catch (e) {
                return undefined;
            }
        }, undefined);
    }
}
EmbeddedLicenseFileScanner.LicenseFiles = ['LICENSE', 'LICENCE', 'License.txt', 'LICENSE.md', 'MIT-LICENSE.txt'];
exports.EmbeddedLicenseFileScanner = EmbeddedLicenseFileScanner;
