"use strict";
const fs = require('fs');
const path = require('path');
class LicenseNameScanner {
    constructor(_pathToLicensesFolder) {
        this._pathToLicensesFolder = _pathToLicensesFolder;
    }
    getLicense(module) {
        if (!module.license) {
            return undefined;
        }
        try {
            let license = module.license.replace(/[:|\/]+/g, '-');
            let licenseFileForModule = fs.readdirSync(this._pathToLicensesFolder).find(f => f === license);
            let pathToFile = path.join(this._pathToLicensesFolder, licenseFileForModule);
            return fs.readFileSync(pathToFile, { encoding: 'utf8' });
        }
        catch (e) {
            return undefined;
        }
    }
}
exports.LicenseNameScanner = LicenseNameScanner;
