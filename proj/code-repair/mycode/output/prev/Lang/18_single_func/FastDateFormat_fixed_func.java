    protected String parseToken(String pattern, int[] indexRef) {
        StringBuilder buffer = new StringBuilder();
        int i = indexRef[0];
        int length = pattern.length();
    
        while (i < length) {
            char c = pattern.charAt(i);
            if (c == '\'') {
                // Handle single quote (') followed by a character or a string of characters
                i++;
                if (i < length && pattern.charAt(i) == '\'') {
                    // Escaped single quote (''), add it to the buffer as-is
                    buffer.append(c);
                    i++;
                } else {
                    // Not an escaped single quote, add the next character to the buffer
                    buffer.append(pattern.charAt(i++));
                }
            } else {
                // Not a single quote, add it to the buffer
                buffer.append(c);
                i++;
            }
        }
    
        indexRef[0] = i;
        return buffer.toString();
    }
