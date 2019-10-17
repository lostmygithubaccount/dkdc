"use strict";
const NodeModulesScanner_1 = require('./ModuleScanners/NodeModulesScanner');
const BowerComponentsScanner_1 = require('./ModuleScanners/BowerComponentsScanner');
const AggregateModuleScanner_1 = require('./ModuleScanners/AggregateModuleScanner');
const ExplicitModulesFileScanner_1 = require('./ModuleScanners/ExplicitModulesFileScanner');
const DotNetPackagesConfigModuleScanner_1 = require('./ModuleScanners/DotNetPackagesConfigModuleScanner');
const DotNetPackageRefModuleScanner_1 = require('./ModuleScanners/DotNetPackageRefModuleScanner');
const CondaChannelScanner_1 = require('./ModuleScanners/CondaChannelScanner');
function createModulesScanner(paths, exclusions) {
    let scanners = paths.map(p => {
        if (p.endsWith('.index.json')) {
            return new CondaChannelScanner_1.CondaChannelScanner(p, exclusions);
        }
        else if (p.endsWith('.json')) {
            return new ExplicitModulesFileScanner_1.ExplicitModulesFileScanner(p);
        }
        else if (p.endsWith('.csproj')) {
            return new DotNetPackageRefModuleScanner_1.DotNetPackageRefModuleScanner(p, exclusions);
        }
        else if (p.endsWith('packages.config')) {
            return new DotNetPackagesConfigModuleScanner_1.DotNetPackagesConfigModuleScanner(p, exclusions);
        }
        else if (p.endsWith('node_modules')) {
            return new NodeModulesScanner_1.NodeModulesScanner(p, exclusions);
        }
        else if (p.endsWith('bower_components')) {
            return new BowerComponentsScanner_1.BowerComponentsScanner(p, exclusions);
        }
        else {
            throw Error('No applicable scanner for path: ' + p);
        }
    });
    return new AggregateModuleScanner_1.AggregateModuleScanner(scanners);
}
exports.createModulesScanner = createModulesScanner;
