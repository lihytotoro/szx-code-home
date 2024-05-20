    public DocumentType(String name, String publicId, String systemId, String baseUri) {
        super(baseUri);
       Validate.notEmpty(name, "Name must not be empty");
        attr("name", name);
        attr("publicId", publicId);
        attr("systemId", systemId);
    }
