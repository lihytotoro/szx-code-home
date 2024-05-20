    public DocumentType(String name, String publicId, String systemId, String baseUri) {
        super(baseUri);
        Validate.notEmpty(name, "String must not be empty");
        attr("name", name);
        attr("publicId", publicId);
        attr("systemId", systemId);
    }
