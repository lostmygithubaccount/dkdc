import {IModule} from '../IModule';
import {IExclusion} from '../ExclusionsListLoaders/IExclusionsListLoader';

export function isModuleExcluded(exclusions: IExclusion[], module: IModule): boolean {
    if (!exclusions) {
        return false;
    }

    let moduleInExclusionsList = exclusions.find(e => e.name === module.name);
    if (!moduleInExclusionsList) {
        return false;
    }

    return !(moduleInExclusionsList.version && moduleInExclusionsList.version !== module.version);
}
