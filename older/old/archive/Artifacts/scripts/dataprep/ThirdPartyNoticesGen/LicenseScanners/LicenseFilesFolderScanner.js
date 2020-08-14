"use strict";
const fs = require('fs');
const path = require('path');
class LicenseFilesFolderScanner {
    constructor(_pathToLicensesFolder) {
        this._pathToLicensesFolder = _pathToLicensesFolder;
    }
    getLicense(module) {
        try {
            let licenseFileForModule = fs.readdirSync(this._pathToLicensesFolder).find(f => f === module.name.replace('/', '-') + '-' + module.version);
            let pathToFile = path.join(this._pathToLicensesFolder, licenseFileForModule);
            return fs.readFileSync(pathToFile, { encoding: 'utf8' });
        }
        catch (e) {
            return undefined;
        }
    }
}
exports.LicenseFilesFolderScanner = LicenseFilesFolderScanner;
