    boolean matchesLetter() {
        if (isEmpty())
            return false;
        char c = input[pos];
       return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
    }
