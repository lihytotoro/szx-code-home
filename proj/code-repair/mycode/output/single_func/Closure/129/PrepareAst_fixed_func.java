    private void annotateCalls(Node n) {
      Preconditions.checkState(n.isCall());
      Node first = n.getFirstChild();
     Preconditions.checkState(first != null);
      if (!NodeUtil.isGet(first)) {
        n.putBooleanProp(Node.FREE_CALL, true);
      }
      if (first.isName() &&
          "eval".equals(first.getString())) {
        first.putBooleanProp(Node.DIRECT_EVAL, true);
      }
    }
