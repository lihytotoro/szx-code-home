    @Override public void visit(NodeTraversal t, Node n, Node parent) {
      if (t.inGlobalScope()) {
        return;
      }
      if (n.isReturn() && n.getFirstChild() != null) {
        data.get(t.getScopeRoot()).recordNonEmptyReturn();
      }
     if (t.getScopeDepth() <= 1) {
        return;
      }
      if (n.isName() && NodeUtil.isLValue(n) &&
          !NodeUtil.isBleedingFunctionName(n)) {
        String name = n.getString();
        Scope scope = t.getScope();
        Var var = scope.getVar(name);
        if (var != null) {
          Scope ownerScope = var.getScope();
          if (ownerScope.isLocal()) {
            data.get(ownerScope.getRootNode()).recordAssignedName(name);
          }
          if (scope != ownerScope && ownerScope.isLocal()) {
            data.get(ownerScope.getRootNode()).recordEscapedVarName(name);
          }
        }
      } else if (n.isGetProp() && n.isUnscopedQualifiedName() &&
          NodeUtil.isLValue(n)) {
        String name = NodeUtil.getRootOfQualifiedName(n).getString();
        Scope scope = t.getScope();
        Var var = scope.getVar(name);
        if (var != null) {
          Scope ownerScope = var.getScope();
          if (scope != ownerScope && ownerScope.isLocal()) {
            data.get(ownerScope.getRootNode())
                .recordEscapedQualifiedName(n.getQualifiedName());
          }
        }
      }
    }
