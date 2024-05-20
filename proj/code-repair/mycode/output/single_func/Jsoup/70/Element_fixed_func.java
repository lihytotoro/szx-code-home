    static boolean preserveWhitespace(Node node) {
        if (node != null && node instanceof Element) {
            Element el = (Element) node;
           if (el.tag.preserveWhitespace())
                return true;
            else if (el.parent() != null && el.parent().tag.preserveWhitespace())
                return true;
        }
        return false;
    }
