    public String absUrl(String attributeKey) {
        Validate.notEmpty(attributeKey);
        String relUrl = attr(attributeKey);
        if (!hasAttr(attributeKey)) {
            return ""; // nothing to make absolute with
        } else {
            URL base;
            try {
                try {
                    base = new URL(baseUri);
                } catch (MalformedURLException e) {
                    URL abs = new URL(relUrl);
                    return abs.toExternalForm();
                }
           } catch (MalformedURLException e) {
                return "";
            }
            try {
                URL abs = new URL(base, relUrl);
                return abs.toExternalForm();
            } catch (MalformedURLException e) {
                return "";
            }
        }
    }
