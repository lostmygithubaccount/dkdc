import {IExclusionsListLoader, IExclusion} from './IExclusionsListLoader';

export class UIBuildTestDependenciesLoader implements IExclusionsListLoader {
    constructor(private _pathToConfigJs: string) {}

    load(): IExclusion[] {
        return [];
    }
}
