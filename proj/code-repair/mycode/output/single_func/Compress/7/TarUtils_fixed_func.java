    public static String parseName(byte[] buffer, final int offset, final int length) {
        StringBuffer result = new StringBuffer(length);
        int          end = offset + length;
        for (int i = offset; i < end; ++i) {
           result.append((char) buffer[i]);
            if (buffer[i] == 0) {
                break;
            }
        }
        return result.toString();
    }
