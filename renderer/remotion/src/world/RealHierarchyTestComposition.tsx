import React from "react";
import { WorldComposition } from "./WorldComposition";
import { loanCompiledWorld } from "./loanCompiledWorldFixture";

export const RealHierarchyTestComposition: React.FC = () => {
  return <WorldComposition world={loanCompiledWorld} />;
};