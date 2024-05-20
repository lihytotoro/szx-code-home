    public JSType caseObjectType(ObjectType type) {
      if (value.equals("function")) {
        JSType ctorType = getNativeType(U2U_CONSTRUCTOR_TYPE);
       return resultEqualsValue && ctorType.isSubtype(type) ? type : null;
      }
      return matchesExpectation("object") ? type : null;
    }
