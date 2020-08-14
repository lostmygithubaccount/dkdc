import {IModuleScanner} from './ModuleScanners/IModuleScanner';
import {NodeModulesScanner} from './ModuleScanners/NodeModulesScanner';
import {BowerComponentsScanner} from './ModuleScanners/BowerComponentsScanner';
import {IExclusion} from './ExclusionsListLoaders/IExclusionsListLoader';
import {AggregateModuleScanner} from './ModuleScanners/AggregateModuleScanner';
import {ExplicitModulesFileScanner} from './ModuleScanners/ExplicitModulesFileScanner';
import {DotNetPackagesConfigModuleScanner} from './ModuleScanners/DotNetPackagesConfigModuleScanner';
import {DotNetPackageRefModuleScanner} from './ModuleScanners/DotNetPackageRefModuleScanner';
import {CondaChannelScanner} from './ModuleScanners/CondaChannelScanner';

export function createModulesScanner(paths: string[], exclusions?: IExclusion[]): IModuleScanner {
    let scanners = paths.map(p => {
        if (p.endsWith('.index.json')) {
            return new CondaChannelScanner(p, exclusions);
        } else if (p.endsWith('.json')) {
            return new ExplicitModulesFileScanner(p);
        } else if (p.endsWith('.csproj')) {
            return new DotNetPackageRefModuleScanner(p, exclusions);
        } else if (p.endsWith('packages.config')) {
            return new DotNetPackagesConfigModuleScanner(p, exclusions);
        } else if (p.endsWith('node_modules')) {
            return new NodeModulesScanner(p, exclusions);
        } else if (p.endsWith('bower_components')) {
            return new BowerComponentsScanner(p, exclusions);
        } else {
            throw Error('No applicable scanner for path: ' + p);
        }
    });
    return new AggregateModuleScanner(scanners);
}
