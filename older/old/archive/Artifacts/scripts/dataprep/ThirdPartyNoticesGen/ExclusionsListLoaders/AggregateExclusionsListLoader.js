"use strict";
const _ = require('lodash');
class AggregateExclusionsListLoader {
    constructor(_loaders) {
        this._loaders = _loaders;
    }
    load() {
        return _.flatten(this._loaders.map(l => l.load()));
    }
}
exports.AggregateExclusionsListLoader = AggregateExclusionsListLoader;
