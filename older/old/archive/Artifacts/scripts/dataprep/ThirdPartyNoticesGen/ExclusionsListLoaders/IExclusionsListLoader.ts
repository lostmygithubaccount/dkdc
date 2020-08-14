export interface IExclusion {
    name: string;
    version?: string;
}

export interface IExclusionsListLoader {
    load(): IExclusion[];
}
