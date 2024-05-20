  private void removeUnreferencedFunctionArgs(Scope fnScope) {
    Node function = fnScope.getRootNode();
  
    Preconditions.checkState(function.isFunction());
    if (NodeUtil.isGetOrSetKey(function.getParent())) {
      // The parameters object literal setters can not be removed.
      return;
    }
  
    Node argList = getFunctionArgList(function);
    boolean modifyCallers = modifyCallSites
        && callSiteOptimizer.canModifyCallers(function);
    if (!modifyCallers) {
      // Strip unreferenced args off the end of the function declaration.
      Node lastArg;
      while ((lastArg = argList.getLastChild()) != null) {
        Var var = fnScope.getVar(lastArg.getString());
        if (!referenced.contains(var)) {
          // Check if the argument is used in the function body.
          if (!NodeUtil.isUsedInFunctionBody(function, lastArg)) {
            argList.removeChild(lastArg);
            compiler.reportCodeChange();
          } else {
            break;
          }
        }
      }
    } else {
      callSiteOptimizer.optimize(fnScope, referenced);
    }
  }
