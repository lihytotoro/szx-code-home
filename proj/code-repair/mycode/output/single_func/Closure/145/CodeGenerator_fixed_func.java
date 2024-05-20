  private boolean isOneExactlyFunctionOrDo(Node n) {
     return (n.getType() == Token.FUNCTION || n.getType() == Token.DO || n.getType() == Token.VAR);
  }
