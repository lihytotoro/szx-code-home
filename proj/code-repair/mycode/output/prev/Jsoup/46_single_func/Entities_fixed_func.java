    private static boolean canEncode(CoreCharset coreCharset, char c, CharsetEncoder encoder) {
        return encoder.canEncode(Character.toCodePoint(c));
    }
