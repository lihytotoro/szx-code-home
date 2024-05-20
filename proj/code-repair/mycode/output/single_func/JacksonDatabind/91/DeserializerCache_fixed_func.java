    private boolean _hasCustomHandlers(JavaType t) {
        if (t.isContainerType()) {
            JavaType ct = t.getContentType();
            if (ct != null) {
               if (ct.getValueHandler() != null || ct.getTypeHandler() != null) {
                    return true;
                }
            }
        }
        return false;
    }
