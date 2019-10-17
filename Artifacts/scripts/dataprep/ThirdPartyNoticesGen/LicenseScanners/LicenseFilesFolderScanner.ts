import {ILicenseScanner} from './ILicenseScanner';
import {IModule} from '../IModule';
import fs = require('fs');
import path = require('path');

export class LicenseFilesFolderScanner implements ILicenseScanner {
    constructor(private _pathToLicensesFolder: string) {}

    getLicense(module: IModule): string {
        try {
            let licenseFileForModule = fs.readdirSync(this._pathToLicensesFolder).find(f => f === module.name.replace('/', '-') + '-' + module.version);
            let pathToFile = path.join(this._pathToLicensesFolder, licenseFileForModule);
            return fs.readFileSync(pathToFile, {encoding: 'utf8'});
        } catch (e) {
            return undefined;
        }
    }
}
