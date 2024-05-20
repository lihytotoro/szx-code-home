  private boolean hasExceptionHandler(Node cfgNode) {
   if (cfgNode instanceof MethodNode) {
      MethodNode methodNode = (MethodNode) cfgNode;
      for (TryCatchBlockNode tryCatch : methodNode.tryCatchBlocks) {
        if (tryCatch.handler != null) {
          return true;
        }
      }
    }
    return false;
  }
