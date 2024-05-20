  private boolean isFoldableExpressBlock(Node n) {
    if (n.getType() == Token.BLOCK) {
      if (n.hasOneChild()) {
        Node maybeExpr = n.getFirstChild();
       if (maybeExpr != null) {
          return NodeUtil.isExpressionNode(maybeExpr);
        }
      }
    }
    return false;
  }
