"use strict";
const fs = require('fs');
const path = require('path');
const _ = require('lodash');
const IsModuleExcluded_1 = require('./IsModuleExcluded');
class NodeModulesScanner {
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
        if (path.basename(modulePath).startsWith('.')) {
            // Ignore hidden folders
            return [];
        }
        if (path.basename(modulePath).startsWith('@')) {
            // Scoped-module parent folder, just recurse.
            return this.scanPathForModules(modulePath);
        }
        try {
            fs.lstatSync(modulePath);
        }
        catch (e) {
            // Folder does not exist. Ignore.
            return [];
        }
        let packageJsonPath = path.join(modulePath, 'package.json');
        let modules = [];
        try {
            let modulePackageJson = fs.readFileSync(packageJsonPath, { encoding: 'utf8' });
            let moduleInfo = JSON.parse(modulePackageJson);
            let module = { name: moduleInfo.name, version: moduleInfo.version, path: modulePath };
            if (!IsModuleExcluded_1.isModuleExcluded(this._exclusions, module)) {
                modules.push(module);
                let nestedModulesPath = path.join(modulePath, 'node_modules');
                let nestedModules = this.scanPathForModules(nestedModulesPath);
                modules = modules.concat(nestedModules);
            }
        }
        catch (e) {
            throw new Error('Could not identify module for path: ' + modulePath);
        }
        return modules;
    }
}
exports.NodeModulesScanner = NodeModulesScanner;
