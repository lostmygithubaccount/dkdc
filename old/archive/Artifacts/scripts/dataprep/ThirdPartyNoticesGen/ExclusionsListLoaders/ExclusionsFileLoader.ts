import {IExclusionsListLoader, IExclusion} from './IExclusionsListLoader';
import fs = require('fs');

export class ExclusionsFileLoader implements IExclusionsListLoader {
    constructor(private _pathToExclusionsFile: string) {}

    load(): IExclusion[] {
        let exclusionsFileContents = fs.readFileSync(this._pathToExclusionsFile, {encoding: 'utf8'});
        return JSON.parse(exclusionsFileContents);
    }
}
