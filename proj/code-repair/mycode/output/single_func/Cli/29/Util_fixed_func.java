    static String stripLeadingAndTrailingQuotes(String str)
    {
       if (str != null && str.startsWith("\""))
        {
            str = str.substring(1, str.length());
        }
        if (str != null && str.endsWith("\""))
        {
            str = str.substring(0, str.length() - 1);
        }
        return str;
    }
