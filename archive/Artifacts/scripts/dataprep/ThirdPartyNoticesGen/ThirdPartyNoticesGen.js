"use strict";
const fs = require('fs');
const path = require('path');
const yargs = require('yargs');
const ModulesScanners_1 = require('./ModulesScanners');
const LicenseScanners_1 = require('./LicenseScanners');
const ExclusionsListLoaders_1 = require('./ExclusionsListLoaders');
let exclusionsPaths = yargs.argv.exclusionsPaths.split(',').map(p => path.resolve(p));
let exclusionsListLoader = ExclusionsListLoaders_1.createExclusionsListLoader(exclusionsPaths);
let exclusions = exclusionsListLoader.load();
let targetPath = yargs.argv.targetPath;
let paths = targetPath.split(',').map(p => path.resolve(p));
let scanner = ModulesScanners_1.createModulesScanner(paths, exclusions);
let modules = scanner.scan();
let licensesFolder = path.resolve(yargs.argv.licensesFolder);
let licenseScanner = LicenseScanners_1.createLicenseScanner(licensesFolder);
let concatenatedLicenses = '';
let prependFile = path.resolve(yargs.argv.prependFile);
let prependText = fs.readFileSync(prependFile, { encoding: 'utf8' });
concatenatedLicenses += prependText;
let modulesWithMissingLicenses = [];
modules.forEach(module => {
    let license = licenseScanner.getLicense(module);
    if (license) {
        concatenatedLicenses += '--------------------------------------------\n\n';
        concatenatedLicenses += (module.name + ' ' + module.version + '\n\n');
        concatenatedLicenses += license;
        concatenatedLicenses += '\n';
    }
    else {
        modulesWithMissingLicenses.push(module);
    }
});
if (yargs.argv.appendFile) {
    let appendFile = path.resolve(yargs.argv.appendFile);
    let appendText = fs.readFileSync(appendFile, { encoding: 'utf8' });
    concatenatedLicenses += '--------------------------------------------\n\n';
    concatenatedLicenses += appendText;
}
let outputFile = yargs.argv.output;
fs.writeFileSync(outputFile, concatenatedLicenses);
if (modulesWithMissingLicenses.length > 0) {
    console.log('Missing licenses for the following modules:');
    modulesWithMissingLicenses.forEach(m => console.log(m.name + ' ' + m.version));
}
else {
    console.log('Third party licenses placed at: ' + path.resolve(outputFile));
}
process.exit(modulesWithMissingLicenses.length === 0 ? 0 : 1);
