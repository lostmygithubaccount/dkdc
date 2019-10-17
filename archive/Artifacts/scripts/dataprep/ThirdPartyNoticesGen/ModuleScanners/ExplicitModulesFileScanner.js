"use strict";
const fs = require('fs');
class ExplicitModulesFileScanner {
    constructor(_pathToModulesFile) {
        this._pathToModulesFile = _pathToModulesFile;
    }
    scan() {
        let fileContents = fs.readFileSync(this._pathToModulesFile, { encoding: 'utf8' });
        return JSON.parse(fileContents);
    }
}
exports.ExplicitModulesFileScanner = ExplicitModulesFileScanner;
