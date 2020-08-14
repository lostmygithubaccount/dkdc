import {IModule} from '../IModule';

export interface ILicenseScanner {
    getLicense(module: IModule): string;
}
