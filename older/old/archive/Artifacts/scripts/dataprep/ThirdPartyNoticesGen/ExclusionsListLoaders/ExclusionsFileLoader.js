"use strict";
const fs = require('fs');
class ExclusionsFileLoader {
    constructor(_pathToExclusionsFile) {
        this._pathToExclusionsFile = _pathToExclusionsFile;
    }
    load() {
        let exclusionsFileContents = fs.readFileSync(this._pathToExclusionsFile, { encoding: 'utf8' });
        return JSON.parse(exclusionsFileContents);
    }
}
exports.ExclusionsFileLoader = ExclusionsFileLoader;
