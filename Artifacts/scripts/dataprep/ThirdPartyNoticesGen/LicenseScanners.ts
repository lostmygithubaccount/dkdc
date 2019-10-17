import {ILicenseScanner} from './LicenseScanners/ILicenseScanner';
import {EmbeddedLicenseFileScanner} from './LicenseScanners/EmbeddedLicenseFileScanner';
import {AggregateLicenseScanner} from './LicenseScanners/AggregateLicenseScanner';
import {LicenseFilesFolderScanner} from './LicenseScanners/LicenseFilesFolderScanner';
import {LicenseNameScanner} from './LicenseScanners/LicenseNameScanner';

export function createLicenseScanner(licensesFolderPath: string): ILicenseScanner {
    return new AggregateLicenseScanner([
        new EmbeddedLicenseFileScanner(),
        new LicenseFilesFolderScanner(licensesFolderPath),
        new LicenseNameScanner(licensesFolderPath)
    ]);
}
