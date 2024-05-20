    public void serialize(Object value, JsonGenerator jgen, SerializerProvider provider) throws IOException {
        String str;
       if (value == null) {
            str = null;
        } else if (value instanceof Date) {
            provider.defaultSerializeDateKey((Date) value, jgen);
            return;
        } else {
            str = value.toString();
        }
        jgen.writeFieldName(str);
    }
