"use strict";
const UIBuildTestDependenciesLoader_1 = require('./ExclusionsListLoaders/UIBuildTestDependenciesLoader');
const ExclusionsFileLoader_1 = require('./ExclusionsListLoaders/ExclusionsFileLoader');
const AggregateExclusionsListLoader_1 = require('./ExclusionsListLoaders/AggregateExclusionsListLoader');
function createExclusionsListLoader(exclusionsPaths) {
    let loaders = exclusionsPaths.map(p => {
        if (p.endsWith('config.js')) {
            return new UIBuildTestDependenciesLoader_1.UIBuildTestDependenciesLoader(p);
        }
        else if (p.endsWith('.json')) {
            return new ExclusionsFileLoader_1.ExclusionsFileLoader(p);
        }
        else {
            throw Error('Unsupported exclusions file');
        }
    });
    return new AggregateExclusionsListLoader_1.AggregateExclusionsListLoader(loaders);
}
exports.createExclusionsListLoader = createExclusionsListLoader;
