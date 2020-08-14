import fs = require('fs');
import path = require('path');
import {ILicenseScanner} from './ILicenseScanner';
import {IModule} from '../IModule';

export class EmbeddedLicenseFileScanner implements ILicenseScanner {
    private static LicenseFiles = ['LICENSE', 'LICENCE', 'License.txt', 'LICENSE.md', 'MIT-LICENSE.txt'];

    getLicense(module: IModule): string {
        return EmbeddedLicenseFileScanner.LicenseFiles.reduce((licenseRetrieved, fileToCheck) => {
            if (licenseRetrieved) {
                return licenseRetrieved;
            }

            try {
                let licensePath = path.join(module.path, fileToCheck);
                return fs.readFileSync(licensePath, {encoding: 'utf8'});
            } catch (e) {
                return undefined;
            }
        }, undefined);
    }
}
