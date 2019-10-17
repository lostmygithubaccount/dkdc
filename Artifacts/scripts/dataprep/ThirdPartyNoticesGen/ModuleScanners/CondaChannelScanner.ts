import {IModuleScanner} from './IModuleScanner';
import {IModule} from '../IModule';
import {IExclusion} from '../ExclusionsListLoaders/IExclusionsListLoader';
import {isModuleExcluded} from './IsModuleExcluded';
import fs = require('fs');

export class CondaChannelScanner implements IModuleScanner {

    constructor(private _pathToCondaChannelIndex: string, private _exclusions?: IExclusion[]) {}

    scan(): IModule[] {
        let fileContents = fs.readFileSync(this._pathToCondaChannelIndex, {encoding: 'utf8'});
        let index = JSON.parse(fileContents);

        let modules: IModule[] = [];
        for (var pkg in index) {
            let moduleName = index[pkg].name;
            let version = index[pkg].version;

            let module = {name: moduleName, version: version, path: undefined};
            if (!isModuleExcluded(this._exclusions, module)) {
                modules.push(module);
            }
        }

        return modules;
    }
}
