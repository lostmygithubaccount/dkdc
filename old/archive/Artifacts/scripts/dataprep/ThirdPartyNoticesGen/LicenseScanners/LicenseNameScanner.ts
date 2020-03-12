import fs = require('fs');
import path = require('path');
import {ILicenseScanner} from './ILicenseScanner';
import {IModule} from '../IModule';

export class LicenseNameScanner implements ILicenseScanner {
    constructor(private _pathToLicensesFolder: string) {}

    getLicense(module: IModule): string {
        if (!module.license) {
            return undefined;
        }
        try {
            let license = module.license.replace(/[:|\/]+/g, '-');
            let licenseFileForModule = fs.readdirSync(this._pathToLicensesFolder).find(f => f === license);
            let pathToFile = path.join(this._pathToLicensesFolder, licenseFileForModule);
            return fs.readFileSync(pathToFile, {encoding: 'utf8'});
        } catch (e) {
            return undefined;
        }
    }
}