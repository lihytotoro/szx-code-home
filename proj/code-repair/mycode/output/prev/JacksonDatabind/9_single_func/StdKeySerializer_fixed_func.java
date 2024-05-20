    public void serialize(Object value, JsonGenerator jgen, SerializerProvider provider) throws IOException {
        String str;
    
        if (value instanceof Date) {
            provider.defaultSerializeDateKey((Date) value, jgen);
            return;
        } else {
            str = jgen.writeFieldName(value);
        }
        jgen.writeFieldName(str);
    }
