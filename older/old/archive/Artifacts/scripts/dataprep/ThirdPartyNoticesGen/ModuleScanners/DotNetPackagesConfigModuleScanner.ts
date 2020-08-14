import {IModuleScanner} from './IModuleScanner';
import {IModule} from '../IModule';
import fs = require('fs');
import {IExclusion} from '../ExclusionsListLoaders/IExclusionsListLoader';
import {isModuleExcluded} from './IsModuleExcluded';

export class DotNetPackagesConfigModuleScanner implements IModuleScanner {
    constructor(private _pathToPackagesConfig: string, private _exclusions?: IExclusion[]) {}

    scan(): IModule[] {
        let moduleRegex = /<package id="(.+)" version="(\d+(\.\d+)*)".*\/>/g;
        let fileContents = fs.readFileSync(this._pathToPackagesConfig, {encoding: 'utf8'});
        let modules: IModule[] = [];
        let matches = moduleRegex.exec(fileContents);
        while (matches) {
            let module = {name: matches[1], version: matches[2], path: undefined};
            matches = moduleRegex.exec(fileContents);
            if (!module.name.startsWith('System') && !module.name.startsWith('Microsoft') && !isModuleExcluded(this._exclusions, module)) {
                modules.push(module);
            }
        }

        return modules;
    }
}
