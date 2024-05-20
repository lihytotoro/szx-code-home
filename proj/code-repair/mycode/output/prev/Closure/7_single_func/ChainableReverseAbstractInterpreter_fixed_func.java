    public JSType caseObjectType(ObjectType type) {
      if (value.isSubtype(FunctionType.class)) {
        JSType ctorType = getNativeType(U2U_CONSTRUCTOR_TYPE);
        return resultEqualsValue && ctorType.isSubtype(type) ? ctorType : null;
      } else if (value.equals("function")) {
        return matchesExpectation("object") ? type : null;
      } else {
        return null;
      }
    }
