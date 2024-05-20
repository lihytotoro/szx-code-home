    boolean matchesLetter() {
        if (isEmpty())
            return false;
        char c = input[pos];
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || (c >= '\u0080' && c <= '\u00FF');
    }
