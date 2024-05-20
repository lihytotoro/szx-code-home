    protected JavaType _typeFromId(String id, DatabindContext ctxt) throws IOException
    {
        /* 30-Jan-2010, tatu: Most ids are basic class names; so let's first
         *    check if any generics info is added; and only then ask factory
         *    to do translation when necessary
         */
        TypeFactory tf = ctxt.getTypeFactory();
        if (id.indexOf('<') > 0) {
            JavaType t = tf.constructFromCanonical(id);
           if (t != null) {
                return t;
            }
            t = tf.findType(id);
            return t;
        }
        Class<?> cls;
        try {
            cls =  tf.findClass(id);
        } catch (ClassNotFoundException e) {
            if (ctxt instanceof DeserializationContext) {
                DeserializationContext dctxt = (DeserializationContext) ctxt;
                return dctxt.handleUnknownTypeId(_baseType, id, this, "no such class found");
            }
            return null;
        } catch (Exception e) {
            throw new IllegalArgumentException("Invalid type id '"+id+"' (for id type 'Id.class'): "+e.getMessage(), e);
        }
        return tf.constructSpecializedType(_baseType, cls);
    }
