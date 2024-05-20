    protected XmlSerializerProvider(XmlSerializerProvider src) {
        super(src);
       if (src._rootNameLookup != null) {
            _rootNameLookup = src._rootNameLookup;
        }
    }
