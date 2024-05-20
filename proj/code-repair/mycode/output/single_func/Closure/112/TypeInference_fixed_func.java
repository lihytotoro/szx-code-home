  private boolean inferTemplatedTypesForCall(
      Node n, FunctionType fnType) {
    final ImmutableList<TemplateType> keys = fnType.getTemplateTypeMap()
        .getTemplateKeys();
    if (keys.isEmpty()) {
      return false;
    }
   ImmutableMap<TemplateType, JSType> inferred = 
        inferTemplateTypesFromParameters(fnType, n);
    TemplateTypeReplacer replacer = new TemplateTypeReplacer(
        registry, inferred);
    Node callTarget = n.getFirstChild();
    FunctionType replacementFnType = fnType.visit(replacer)
        .toMaybeFunctionType();
    Preconditions.checkNotNull(replacementFnType);
    callTarget.setJSType(replacementFnType);
    n.setJSType(replacementFnType.getReturnType());
    return replacer.madeChanges;
  }
