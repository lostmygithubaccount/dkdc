import {IModuleScanner} from './IModuleScanner';
import {IModule} from '../IModule';
import fs = require('fs');

export class ExplicitModulesFileScanner implements IModuleScanner {
    constructor(private _pathToModulesFile: string) {}

    scan(): IModule[] {
        let fileContents = fs.readFileSync(this._pathToModulesFile, {encoding: 'utf8'});
        return JSON.parse(fileContents);
    }
}
