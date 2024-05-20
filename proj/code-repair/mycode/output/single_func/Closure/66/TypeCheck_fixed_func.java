  public void visit(NodeTraversal t, Node n, Node parent) {
    JSType childType;
    JSType leftType, rightType;
    Node left, right;
    boolean typeable = true;
    switch (n.getType()) {
      case Token.NAME:
        typeable = visitName(t, n, parent);
        break;
      case Token.LP:
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
        if (!NodeUtil.isObjectLitKey(n, n.getParent())) {
          ensureTyped(t, n, STRING_TYPE);
         } else {
            ensureTyped(t, n);
        }
        break;
      case Token.GET:
      case Token.SET:
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
        typeable = false;
        break;
      case Token.VAR:
        visitVar(t, n);
        typeable = false;
        break;
      case Token.NEW:
        visitNew(t, n);
        typeable = true;
        break;
      case Token.CALL:
        visitCall(t, n);
        typeable = !NodeUtil.isExpressionNode(parent);
        break;
      case Token.RETURN:
        visitReturn(t, n);
        typeable = false;
        break;
      case Token.DEC:
      case Token.INC:
        left = n.getFirstChild();
        validator.expectNumber(
            t, left, getJSType(left), "increment/decrement");
        ensureTyped(t, n, NUMBER_TYPE);
        break;
      case Token.NOT:
        ensureTyped(t, n, BOOLEAN_TYPE);
        break;
      case Token.VOID:
        ensureTyped(t, n, VOID_TYPE);
        break;
      case Token.TYPEOF:
        ensureTyped(t, n, STRING_TYPE);
        break;
      case Token.BITNOT:
        childType = getJSType(n.getFirstChild());
        if (!childType.matchesInt32Context()) {
          report(t, n, BIT_OPERATION, NodeUtil.opToStr(n.getType()),
              childType.toString());
        }
        ensureTyped(t, n, NUMBER_TYPE);
        break;
      case Token.POS:
      case Token.NEG:
        left = n.getFirstChild();
        validator.expectNumber(t, left, getJSType(left), "sign operator");
        ensureTyped(t, n, NUMBER_TYPE);
        break;
      case Token.EQ:
      case Token.NE: {
        leftType = getJSType(n.getFirstChild());
        rightType = getJSType(n.getLastChild());
        JSType leftTypeRestricted = leftType.restrictByNotNullOrUndefined();
        JSType rightTypeRestricted = rightType.restrictByNotNullOrUndefined();
        TernaryValue result =
            leftTypeRestricted.testForEquality(rightTypeRestricted);
        if (result != TernaryValue.UNKNOWN) {
          if (n.getType() == Token.NE) {
            result = result.not();
          }
          report(t, n, DETERMINISTIC_TEST, leftType.toString(),
              rightType.toString(), result.toString());
        }
        ensureTyped(t, n, BOOLEAN_TYPE);
        break;
      }
      case Token.SHEQ:
      case Token.SHNE: {
        leftType = getJSType(n.getFirstChild());
        rightType = getJSType(n.getLastChild());
        JSType leftTypeRestricted = leftType.restrictByNotNullOrUndefined();
        JSType rightTypeRestricted = rightType.restrictByNotNullOrUndefined();
        if (!leftTypeRestricted.canTestForShallowEqualityWith(
                rightTypeRestricted)) {
          report(t, n, DETERMINISTIC_TEST_NO_RESULT, leftType.toString(),
              rightType.toString());
        }
        ensureTyped(t, n, BOOLEAN_TYPE);
        break;
      }
      case Token.LT:
      case Token.LE:
      case Token.GT:
      case Token.GE:
        leftType = getJSType(n.getFirstChild());
        rightType = getJSType(n.getLastChild());
        if (rightType.isNumber()) {
          validator.expectNumber(
              t, n, leftType, "left side of numeric comparison");
        } else if (leftType.isNumber()) {
          validator.expectNumber(
              t, n, rightType, "right side of numeric comparison");
        } else if (leftType.matchesNumberContext() &&
                   rightType.matchesNumberContext()) {
        } else {
          String message = "left side of comparison";
          validator.expectString(t, n, leftType, message);
          validator.expectNotNullOrUndefined(
              t, n, leftType, message, getNativeType(STRING_TYPE));
          message = "right side of comparison";
          validator.expectString(t, n, rightType, message);
          validator.expectNotNullOrUndefined(
              t, n, rightType, message, getNativeType(STRING_TYPE));
        }
        ensureTyped(t, n, BOOLEAN_TYPE);
        break;
      case Token.IN:
        left = n.getFirstChild();
        right = n.getLastChild();
        leftType = getJSType(left);
        rightType = getJSType(right);
        validator.expectObject(t, n, rightType, "'in' requires an object");
        validator.expectString(t, left, leftType, "left side of 'in'");
        ensureTyped(t, n, BOOLEAN_TYPE);
        break;
      case Token.INSTANCEOF:
        left = n.getFirstChild();
        right = n.getLastChild();
        leftType = getJSType(left);
        rightType = getJSType(right).restrictByNotNullOrUndefined();
        validator.expectAnyObject(
            t, left, leftType, "deterministic instanceof yields false");
        validator.expectActualObject(
            t, right, rightType, "instanceof requires an object");
        ensureTyped(t, n, BOOLEAN_TYPE);
        break;
      case Token.ASSIGN:
        visitAssign(t, n);
        typeable = false;
        break;
      case Token.ASSIGN_LSH:
      case Token.ASSIGN_RSH:
      case Token.ASSIGN_URSH:
      case Token.ASSIGN_DIV:
      case Token.ASSIGN_MOD:
      case Token.ASSIGN_BITOR:
      case Token.ASSIGN_BITXOR:
      case Token.ASSIGN_BITAND:
      case Token.ASSIGN_SUB:
      case Token.ASSIGN_ADD:
      case Token.ASSIGN_MUL:
      case Token.LSH:
      case Token.RSH:
      case Token.URSH:
      case Token.DIV:
      case Token.MOD:
      case Token.BITOR:
      case Token.BITXOR:
      case Token.BITAND:
      case Token.SUB:
      case Token.ADD:
      case Token.MUL:
        visitBinaryOperator(n.getType(), t, n);
        break;
      case Token.DELPROP:
        if (!isReference(n.getFirstChild())) {
          report(t, n, BAD_DELETE);
        }
        ensureTyped(t, n, BOOLEAN_TYPE);
        break;
      case Token.CASE:
        JSType switchType = getJSType(parent.getFirstChild());
        JSType caseType = getJSType(n.getFirstChild());
        validator.expectSwitchMatchesCase(t, n, switchType, caseType);
        typeable = false;
        break;
      case Token.WITH: {
        Node child = n.getFirstChild();
        childType = getJSType(child);
        validator.expectObject(
            t, child, childType, "with requires an object");
        typeable = false;
        break;
      }
      case Token.FUNCTION:
        visitFunction(t, n);
        break;
      case Token.LABEL:
      case Token.LABEL_NAME:
      case Token.SWITCH:
      case Token.BREAK:
      case Token.CATCH:
      case Token.TRY:
      case Token.SCRIPT:
      case Token.EXPR_RESULT:
      case Token.BLOCK:
      case Token.EMPTY:
      case Token.DEFAULT:
      case Token.CONTINUE:
      case Token.DEBUGGER:
      case Token.THROW:
        typeable = false;
        break;
      case Token.DO:
      case Token.FOR:
      case Token.IF:
      case Token.WHILE:
        typeable = false;
        break;
      case Token.AND:
      case Token.HOOK:
      case Token.OBJECTLIT:
      case Token.OR:
        if (n.getJSType() != null) { // If we didn't run type inference.
          ensureTyped(t, n);
        } else {
          if ((n.getType() == Token.OBJECTLIT)
              && (parent.getJSType() instanceof EnumType)) {
            ensureTyped(t, n, parent.getJSType());
          } else {
            ensureTyped(t, n);
          }
        }
        if (n.getType() == Token.OBJECTLIT) {
          for (Node key : n.children()) {
            visitObjLitKey(t, key, n);
          }
        }
        break;
      default:
        report(t, n, UNEXPECTED_TOKEN, Token.name(n.getType()));
        ensureTyped(t, n);
        break;
    }
    typeable = typeable && !inExterns;
    if (typeable) {
      doPercentTypedAccounting(t, n);
    }
    checkNoTypeCheckSection(n, false);
  }
