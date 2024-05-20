    boolean isAssignedOnceInLifetime() {
      Reference ref = getOneAndOnlyAssignment();
      if (ref == null) {
        return false;
      }
      for (BasicBlock block = ref.getBasicBlock();
           block != null; block = block.getParent()) {
        if (block.isFunction) {
         if (block.isLoop) {
            return false;
          }
          break;
        } else if (block.isLoop) {
          return false;
        }
      }
      return true;
    }
