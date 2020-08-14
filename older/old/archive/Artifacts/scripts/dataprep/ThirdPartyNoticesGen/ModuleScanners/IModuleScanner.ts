import {IModule} from '../IModule';

export interface IModuleScanner {
    scan(): IModule[];
}
