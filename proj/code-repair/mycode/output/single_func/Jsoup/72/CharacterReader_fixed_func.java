    private static String cacheString(final char[] charBuf, final String[] stringCache, final int start, final int count) {
        if (count > maxStringCacheLen)
            return new String(charBuf, start, count);
        int hash = 0;
        int offset = start;
        for (int i = 0; i < count; i++) {
            hash = 31 * hash + charBuf[offset++];
        }
        final int index = hash & stringCache.length - 1;
        String cached = stringCache[index];
        if (cached == null) { // miss, add
            cached = new String(charBuf, start, count);
            stringCache[index] = cached;
        } else { // hashcode hit, check equality
            if (rangeEquals(charBuf, start, count, cached)) { // hit
                return cached;
            } else { // hashcode conflict
                cached = new String(charBuf, start, count);
                stringCache[index] = cached; // update the cache, as recently used strings are more likely to show up again
            }
        }
        return cached;
    }
