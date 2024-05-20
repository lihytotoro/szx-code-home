  private Node parseContextTypeExpression(JsDocToken token) {
      if (token.type == JsDocTokenType.NEW) {
          // Handle the case where the type expression starts with "new:"
          return parseTypeName(token);
      } else {
          // Handle the case where the type expression does not start with "new:"
          return parseTypeName(token);
      }
  }
