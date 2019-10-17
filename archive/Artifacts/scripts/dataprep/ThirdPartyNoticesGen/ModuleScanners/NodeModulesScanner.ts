import fs = require('fs');
import path = require('path');
import _ = require('lodash');
import {IModuleScanner} from './IModuleScanner';
import {IModule} from '../IModule';
import {isModuleExcluded} from './IsModuleExcluded';

export class NodeModulesScanner implements IModuleScanner {
    constructor(private _path: string, private _exclusions?: {name: string, version?: string}[]) {}

    scan(): IModule[] {
        return this.scanPathForModules(this._path);
    }

    private scanPathForModules(folderPath: string): IModule[] {
        let folderContents: string[] = [];
        try {
            folderContents = fs.readdirSync(folderPath);
        } catch (e) {
            // Folder does not exist. Ignore.
            return [];
        }

        let modules = folderContents.map(sd => this.scanModule(path.join(folderPath, sd)));
        return _.flattenDeep<IModule>(modules);
    }

    private scanModule(modulePath: string): IModule[] {
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
        } catch (e) {
            // Folder does not exist. Ignore.
            return [];
        }

        let packageJsonPath = path.join(modulePath, 'package.json');
        let modules: IModule[] = [];
        try {
            let modulePackageJson = fs.readFileSync(packageJsonPath, {encoding: 'utf8'});
            let moduleInfo = JSON.parse(modulePackageJson);
            let module: IModule = {name: moduleInfo.name, version: moduleInfo.version, path: modulePath};
            if (!isModuleExcluded(this._exclusions, module)) {
                modules.push(module);
                let nestedModulesPath = path.join(modulePath, 'node_modules');
                let nestedModules = this.scanPathForModules(nestedModulesPath);
                modules = modules.concat(nestedModules);
            }
        } catch (e) {
            throw new Error('Could not identify module for path: ' + modulePath);
        }

        return modules;
    }
}
