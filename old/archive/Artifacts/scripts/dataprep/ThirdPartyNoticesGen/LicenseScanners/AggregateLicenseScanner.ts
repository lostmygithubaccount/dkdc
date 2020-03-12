import {ILicenseScanner} from './ILicenseScanner';
import {IModule} from '../IModule';

export class AggregateLicenseScanner implements ILicenseScanner {
    constructor(private _scanners: ILicenseScanner[]) {}

    getLicense(module: IModule): string {
        return this._scanners.reduce((license, scanner) => {
            if (license) {
                return license;
            }

            return scanner.getLicense(module);
        }, undefined);
    }
}
