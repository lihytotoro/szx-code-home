    public boolean hasAttr(String attributeKey) {
        Validate.notNull(attributeKey, "attributeKey cannot be null");
        return attributes.hasKey(attributeKey);
    }
