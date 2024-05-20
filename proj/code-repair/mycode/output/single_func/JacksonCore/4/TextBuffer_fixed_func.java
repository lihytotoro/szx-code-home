    public char[] expandCurrentSegment()
    {
        final char[] curr = _currentSegment;
        final int len = curr.length;
       int newLen = (len == MAX_SEGMENT_LEN) ? MAX_SEGMENT_LEN : Math.min(MAX_SEGMENT_LEN, len + (len >> 1));
        return (_currentSegment = Arrays.copyOf(curr, newLen));
    }
