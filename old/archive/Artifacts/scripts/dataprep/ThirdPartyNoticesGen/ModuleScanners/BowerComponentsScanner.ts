import fs = require('fs');
import path = require('path');
import _ = require('lodash');
import {IModuleScanner} from './IModuleScanner';
import {IModule} from '../IModule';
import {isModuleExcluded} from './IsModuleExcluded';

export class BowerComponentsScanner implements IModuleScanner {
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
        let bowerJsonPath = path.join(modulePath, 'bower.json');
        let modules: IModule[] = [];
        try {
            let moduleBowerJson = fs.readFileSync(bowerJsonPath, {encoding: 'utf8'});
            let moduleInfo = JSON.parse(moduleBowerJson);
            let module: IModule = {
                name: moduleInfo.name,
                version: moduleInfo.version,
                path: modulePath,
                license: moduleInfo.license
            };
            if (!isModuleExcluded(this._exclusions, module)) {
                modules.push(module);
            }
        } catch (e) {
            throw new Error('Could not identify module for path: ' + modulePath);
        }

        return modules;
    }
}