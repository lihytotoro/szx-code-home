  String getReadableJSTypeName(Node n, boolean dereference) {
  JSType type = getJSType(n);
  if (n.isGetProp()) {
    ObjectType objectType = getJSType(n.getFirstChild()).dereference();
    if (objectType != null) {
      String propName = n.getLastChild().getString();
      if (objectType.getConstructor() != null &&
          objectType.getConstructor().isInterface()) {
        objectType = FunctionType.getTopDefiningInterface(
            objectType, propName);
      } else {
        while (objectType != null && !objectType.hasOwnProperty(propName)) {
          objectType = objectType.getImplicitPrototype();
        }
      }
      if (objectType != null &&
          (objectType.getConstructor() != null ||
           objectType.isFunctionPrototypeType())) {
        return objectType.toString() + "." + propName;
      }
    }
  }
  if (dereference) {
    ObjectType dereferenced = type.dereference();
    if (dereferenced != null) {
      type =
    String qualifiedName = n.getQualifiedName();
    if (qualifiedName != null) {
      return qualifiedName;
    } else if (type.isFunctionType()) {
      return "function";
    } else {
      return type.toString();
    }
  }
