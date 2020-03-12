"use strict";
const fs = require('fs');
const IsModuleExcluded_1 = require('./IsModuleExcluded');
class DotNetPackagesConfigModuleScanner {
    constructor(_pathToPackagesConfig, _exclusions) {
        this._pathToPackagesConfig = _pathToPackagesConfig;
        this._exclusions = _exclusions;
    }
    scan() {
        let moduleRegex = /<package id="(.+)" version="(\d+(\.\d+)*)".*\/>/g;
        let fileContents = fs.readFileSync(this._pathToPackagesConfig, { encoding: 'utf8' });
        let modules = [];
        let matches = moduleRegex.exec(fileContents);
        while (matches) {
            let module = { name: matches[1], version: matches[2], path: undefined };
            matches = moduleRegex.exec(fileContents);
            if (!module.name.startsWith('System') && !module.name.startsWith('Microsoft') && !IsModuleExcluded_1.isModuleExcluded(this._exclusions, module)) {
                modules.push(module);
            }
        }
        return modules;
    }
}
exports.DotNetPackagesConfigModuleScanner = DotNetPackagesConfigModuleScanner;
