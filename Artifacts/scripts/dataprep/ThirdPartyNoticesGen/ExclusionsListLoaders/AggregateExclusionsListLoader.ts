import {IExclusionsListLoader, IExclusion} from './IExclusionsListLoader';
import _ = require('lodash');

export class AggregateExclusionsListLoader implements IExclusionsListLoader {
    constructor(private _loaders: IExclusionsListLoader[]) {}

    load(): IExclusion[] {
        return _.flatten(this._loaders.map(l => l.load()));
    }
}
