    private static boolean rangeEquals(char[] charBuf, int start, int count, String cached) {
        return cached.regionMatches(true, 0, charBuf, start, count);
    }