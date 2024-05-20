        public ObjectNode deserialize(JsonParser p, DeserializationContext ctxt) throws IOException
        {
           if (p.currentToken() == JsonToken.START_OBJECT) {
                p.nextToken();
                return deserializeObject(p, ctxt, ctxt.getNodeFactory());
            }
            if (p.currentToken() == JsonToken.FIELD_NAME) {
                return deserializeObject(p, ctxt, ctxt.getNodeFactory());
            }
            throw ctxt.mappingException(ObjectNode.class);
         }
