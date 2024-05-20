    public boolean hasAttr(String attributeKey) {
        Validate.notNull(attributeKey);
       Validate.notEmpty(attributeKey);
        return attributes.hasKey(attributeKey);
    }
