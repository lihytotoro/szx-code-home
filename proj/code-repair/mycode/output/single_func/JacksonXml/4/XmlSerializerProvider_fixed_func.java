    protected void _serializeXmlNull(JsonGenerator jgen) throws IOException
    {
       if (jgen instanceof ToXmlJsonGenerator) {
            _initWithRootName((ToXmlJsonGenerator) jgen, ROOT_NAME_FOR_NULL);
        }
        super.serializeValue(jgen, null);
    }
