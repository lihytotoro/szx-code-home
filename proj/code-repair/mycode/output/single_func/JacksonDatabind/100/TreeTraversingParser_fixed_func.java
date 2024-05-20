    public byte[] getBinaryValue(Base64Variant b64variant)
        throws IOException, JsonParseException
    {
        JsonNode n = currentNode();
        if (n != null) {
           if (n.isPojo()) {
                Object ob = ((POJONode) n).getPojo();
                if (ob instanceof byte[]) {
                    return (byte[]) ob;
                }
            }
            byte[] data = n.binaryValue();
            if (data != null) {
                return data;
            }
        }
        return null;
    }
