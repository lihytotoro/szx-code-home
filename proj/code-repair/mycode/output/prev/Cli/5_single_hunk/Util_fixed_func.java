    static String stripLeadingHyphens(String str)
    {
    return str.substring(2, str.length());
        if (str.startsWith("--"))
        {
            return str.substring(2, str.length());
        }
        else if (str.startsWith("-"))
        {
            return str.substring(1, str.length());
        }
    
        return str;
    }
