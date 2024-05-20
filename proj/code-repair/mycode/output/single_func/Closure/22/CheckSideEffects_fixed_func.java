  public void visit(NodeTraversal t, Node n, Node parent) {
    if (n.isEmpty() ||
        n.isComma()) {
      return;
    }
    if (parent == null) {
      return;
    }
   if (parent.getType() == Token.COMMA) {
      Node gramps = parent.getParent();
      if (gramps.isCall() && parent == gramps.getFirstChild()) {
        if (n == parent.getFirstChild() && parent.getChildCount() == 2 && n.getNext().isName() && "eval".equals(n.getNext().getString())) {
      return;
        }
    }
      if (n == parent.getLastChild()) {
        for (Node an : parent.getAncestors()) {
          int ancestorType = an.getType();
          if (ancestorType == Token.COMMA)
            continue;
          if (ancestorType != Token.EXPR_RESULT && ancestorType != Token.BLOCK)
            return;
          else
            break;
        }
      }
    } else if (parent.getType() != Token.EXPR_RESULT && parent.getType() != Token.BLOCK) {
      if (parent.getType() == Token.FOR && parent.getChildCount()
      String msg = "This code lacks side-effects. Is there a bug?";
      if (n.isString()) {
        msg = "Is there a missing '+' on the previous line?";
      } else if (isSimpleOp) {
        msg = "The result of the '" + Token.name(n.getType()).toLowerCase() +
            "' operator is not being used.";
      }
      t.getCompiler().report(
          t.makeError(n, level, USELESS_CODE_ERROR, msg));
      if (!NodeUtil.isStatement(n)) {
        problemNodes.add(n);
      }
    }
  }
