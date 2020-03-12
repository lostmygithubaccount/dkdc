"use strict";
const _ = require('lodash');
class AggregateModuleScanner {
    constructor(_scanners) {
        this._scanners = _scanners;
    }
    scan() {
        return _.uniqBy(_.flatten(this._scanners.map(s => s.scan())), m => m.name + m.version + m.path);
    }
}
exports.AggregateModuleScanner = AggregateModuleScanner;
