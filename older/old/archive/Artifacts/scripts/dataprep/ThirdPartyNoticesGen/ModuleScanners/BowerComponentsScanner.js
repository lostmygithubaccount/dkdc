"use strict";
const fs = require('fs');
const path = require('path');
const _ = require('lodash');
const IsModuleExcluded_1 = require('./IsModuleExcluded');
class BowerComponentsScanner {
    constructor(_path, _exclusions) {
        this._path = _path;
        this._exclusions = _exclusions;
    }
    scan() {
        return this.scanPathForModules(this._path);
    }
    scanPathForModules(folderPath) {
        let folderContents = [];
        try {
            folderContents = fs.readdirSync(folderPath);
        }
        catch (e) {
            // Folder does not exist. Ignore.
            return [];
        }
        let modules = folderContents.map(sd => this.scanModule(path.join(folderPath, sd)));
        return _.flattenDeep(modules);
    }
    scanModule(modulePath) {
        let bowerJsonPath = path.join(modulePath, 'bower.json');
        let modules = [];
        try {
            let moduleBowerJson = fs.readFileSync(bowerJsonPath, { encoding: 'utf8' });
            let moduleInfo = JSON.parse(moduleBowerJson);
            let module = {
                name: moduleInfo.name,
                version: moduleInfo.version,
                path: modulePath,
                license: moduleInfo.license
            };
            if (!IsModuleExcluded_1.isModuleExcluded(this._exclusions, module)) {
                modules.push(module);
            }
        }
        catch (e) {
            throw new Error('Could not identify module for path: ' + modulePath);
        }
        return modules;
    }
}
exports.BowerComponentsScanner = BowerComponentsScanner;
