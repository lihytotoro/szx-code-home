    static String stripLeadingAndTrailingQuotes(String str) {
        while (str.startsWith("\"")) {
            str = str.substring(1, str.length());
        }
        while (str.endsWith("\"")) {
            str = str.substring(0, str.length() - 1);
        }
        return str;
    }
