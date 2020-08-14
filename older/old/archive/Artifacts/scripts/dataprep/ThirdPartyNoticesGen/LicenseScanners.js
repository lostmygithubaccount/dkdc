"use strict";
const EmbeddedLicenseFileScanner_1 = require('./LicenseScanners/EmbeddedLicenseFileScanner');
const AggregateLicenseScanner_1 = require('./LicenseScanners/AggregateLicenseScanner');
const LicenseFilesFolderScanner_1 = require('./LicenseScanners/LicenseFilesFolderScanner');
const LicenseNameScanner_1 = require('./LicenseScanners/LicenseNameScanner');
function createLicenseScanner(licensesFolderPath) {
    return new AggregateLicenseScanner_1.AggregateLicenseScanner([
        new EmbeddedLicenseFileScanner_1.EmbeddedLicenseFileScanner(),
        new LicenseFilesFolderScanner_1.LicenseFilesFolderScanner(licensesFolderPath),
        new LicenseNameScanner_1.LicenseNameScanner(licensesFolderPath)
    ]);
}
exports.createLicenseScanner = createLicenseScanner;
