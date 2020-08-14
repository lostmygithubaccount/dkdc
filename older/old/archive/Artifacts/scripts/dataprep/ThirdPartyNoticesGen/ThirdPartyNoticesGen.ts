import fs = require('fs');
import path = require('path');
import yargs = require('yargs');
import {IModule} from './IModule';
import {createModulesScanner} from './ModulesScanners';
import {createLicenseScanner} from './LicenseScanners';
import {createExclusionsListLoader} from './ExclusionsListLoaders';

let exclusionsPaths = yargs.argv.exclusionsPaths.split(',').map(p => path.resolve(p));
let exclusionsListLoader = createExclusionsListLoader(exclusionsPaths);
let exclusions = exclusionsListLoader.load();

let targetPath: string = yargs.argv.targetPath;
let paths: string[] = targetPath.split(',').map(p => path.resolve(p));
let scanner = createModulesScanner(paths, exclusions);
let modules = scanner.scan();

let licensesFolder: string = path.resolve(yargs.argv.licensesFolder);
let licenseScanner = createLicenseScanner(licensesFolder);

let concatenatedLicenses = '';
let prependFile: string = path.resolve(yargs.argv.prependFile);
let prependText = fs.readFileSync(prependFile, {encoding: 'utf8'});
concatenatedLicenses += prependText;

let modulesWithMissingLicenses: IModule[] = [];
modules.forEach(module => {
    let license = licenseScanner.getLicense(module);
    if (license) {
        concatenatedLicenses += '--------------------------------------------\n\n';
        concatenatedLicenses += (module.name + ' ' + module.version + '\n\n');
        concatenatedLicenses += license;
        concatenatedLicenses += '\n';
    } else {
        modulesWithMissingLicenses.push(module);
    }
});

if (yargs.argv.appendFile) {
    let appendFile = path.resolve(yargs.argv.appendFile);
    let appendText = fs.readFileSync(appendFile, {encoding: 'utf8'});
    concatenatedLicenses += '--------------------------------------------\n\n';
    concatenatedLicenses += appendText;
}

let outputFile = yargs.argv.output;
fs.writeFileSync(outputFile, concatenatedLicenses);
if (modulesWithMissingLicenses.length > 0) {
    console.log('Missing licenses for the following modules:');
    modulesWithMissingLicenses.forEach(m => console.log(m.name + ' ' + m.version));
} else {
    console.log('Third party licenses placed at: '  + path.resolve(outputFile));
}

process.exit(modulesWithMissingLicenses.length === 0 ? 0 : 1);
