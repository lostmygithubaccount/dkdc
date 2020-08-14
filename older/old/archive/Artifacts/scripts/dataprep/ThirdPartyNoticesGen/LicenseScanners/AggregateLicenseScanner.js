"use strict";
class AggregateLicenseScanner {
    constructor(_scanners) {
        this._scanners = _scanners;
    }
    getLicense(module) {
        return this._scanners.reduce((license, scanner) => {
            if (license) {
                return license;
            }
            return scanner.getLicense(module);
        }, undefined);
    }
}
exports.AggregateLicenseScanner = AggregateLicenseScanner;
