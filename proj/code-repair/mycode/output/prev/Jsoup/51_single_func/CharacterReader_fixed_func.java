    boolean matchesLetter() {
        if (isEmpty())
            return false;
        char c = input[pos];
        return Character.isLetter(c);
    }
