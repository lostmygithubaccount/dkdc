import {IModuleScanner} from './IModuleScanner';
import {IModule} from '../IModule';
import _ = require('lodash');

export class AggregateModuleScanner implements IModuleScanner {
    constructor(private _scanners: IModuleScanner[]) {}

    scan(): IModule[] {
        return _.uniqBy(_.flatten(this._scanners.map(s => s.scan())), m => m.name + m.version + m.path);
    }
}
