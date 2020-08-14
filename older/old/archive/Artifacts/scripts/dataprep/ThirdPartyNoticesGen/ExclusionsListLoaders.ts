import {IExclusion, IExclusionsListLoader} from './ExclusionsListLoaders/IExclusionsListLoader';
import {UIBuildTestDependenciesLoader} from './ExclusionsListLoaders/UIBuildTestDependenciesLoader';
import {ExclusionsFileLoader} from './ExclusionsListLoaders/ExclusionsFileLoader';
import {AggregateExclusionsListLoader} from './ExclusionsListLoaders/AggregateExclusionsListLoader';

export {IExclusion, IExclusionsListLoader};

export function createExclusionsListLoader(exclusionsPaths: string[]): IExclusionsListLoader {
    let loaders = exclusionsPaths.map(p => {
        if (p.endsWith('config.js')) {
            return new UIBuildTestDependenciesLoader(p);
        } else if (p.endsWith('.json')) {
            return new ExclusionsFileLoader(p);
        } else {
            throw Error('Unsupported exclusions file');
        }
    });
    return new AggregateExclusionsListLoader(loaders);
}
