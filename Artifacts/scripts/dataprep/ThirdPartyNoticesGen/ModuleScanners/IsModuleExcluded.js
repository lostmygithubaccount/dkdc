"use strict";
function isModuleExcluded(exclusions, module) {
    if (!exclusions) {
        return false;
    }
    let moduleInExclusionsList = exclusions.find(e => e.name === module.name);
    if (!moduleInExclusionsList) {
        return false;
    }
    return !(moduleInExclusionsList.version && moduleInExclusionsList.version !== module.version);
}
exports.isModuleExcluded = isModuleExcluded;
