"use strict";
const IsModuleExcluded_1 = require('./IsModuleExcluded');
const fs = require('fs');
class CondaChannelScanner {
    constructor(_pathToCondaChannelIndex, _exclusions) {
        this._pathToCondaChannelIndex = _pathToCondaChannelIndex;
        this._exclusions = _exclusions;
    }
    scan() {
        let fileContents = fs.readFileSync(this._pathToCondaChannelIndex, { encoding: 'utf8' });
        let index = JSON.parse(fileContents);
        let modules = [];
        for (var pkg in index) {
            let moduleName = index[pkg].name;
            let version = index[pkg].version;
            let module = { name: moduleName, version: version, path: undefined };
            if (!IsModuleExcluded_1.isModuleExcluded(this._exclusions, module)) {
                modules.push(module);
            }
        }
        return modules;
    }
}
exports.CondaChannelScanner = CondaChannelScanner;
