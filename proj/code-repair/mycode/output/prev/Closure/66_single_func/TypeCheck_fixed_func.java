  public void visit(NodeTraversal t, Node n, Node parent) {
    JSType childType;
    JSType leftType, rightType;
    Node left, right;
    // To be explicitly set to false if the node is not typeable.
    boolean typeable = true;
  
    switch (n.getType()) {
      case Token.NAME:
        typeable = visitName(t, n, parent);
        break;
  
      case Token.LP:
        // If this is under a FUNCTION node, it is a parameter list and can be
        // ignored here.
        if (parent.getType() != Token.FUNCTION) {
          ensureTyped(t, n, getJSType(n.getFirstChild()));
        } else {
          typeable = false;
        }
        break;
  
      case Token.COMMA:
        ensureTyped(t, n, getJSType(n.getLastChild()));
        break;
  
      case Token.TRUE:
      case Token.FALSE:
        ensureTyped(t, n, BOOLEAN_TYPE);
        break;
  
      case Token.THIS:
        ensureTyped(t, n, t.getScope().getTypeOfThis());
        break;
  
      case Token.REF_SPECIAL:
        ensureTyped(t, n);
        break;
  
      case Token.GET_REF:
        ensureTyped(t, n, getJSType(n.getFirstChild()));
        break;
  
      case Token.NULL:
        ensureTyped(t, n, NULL_TYPE);
        break;
  
      case Token.NUMBER:
        ensureTyped(t, n, NUMBER_TYPE);
        break;
  
      case Token.STRING:
        // Object literal keys are handled with OBJECTLIT
        if (!NodeUtil.isObjectLitKey(n, n.getParent())) {
          ensureTyped(t, n, STRING_TYPE);
          // Object literal keys are not typeable
        }
        break;
  
      case Token.GET:
      case Token.SET:
        // Object literal keys are handled with OBJECTLIT
        break;
  
      case Token.ARRAYLIT:
        ensureTyped(t, n, ARRAY_TYPE);
        break;
  
      case Token.REGEXP:
        ensureTyped(t, n, REGEXP_TYPE);
        break;
  
      case Token.GETPROP:
        visitGetProp(t, n, parent);
        typeable = !(parent.getType() == Token.ASSIGN &&
                     parent.getFirstChild() == n);
        break;
  
      case Token.GETELEM:
        visitGetElem(t, n);
        // The type of GETELEM is always unknown, so no point counting that.
        // If that unknown leaks elsewhere (say by an assignment to another
        // variable), then it will be counted.
        typeable = false;
        break;
  
      case Token.VAR:
        visitVar(t, n);
        typeable = false
