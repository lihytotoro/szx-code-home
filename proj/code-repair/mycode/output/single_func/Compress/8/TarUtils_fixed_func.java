    public static long parseOctal(final byte[] buffer, final int offset, final int length) {
        long    result = 0;
       int     end = offset + length;
        int     start = offset;
        for (int i = start; i < end; i++){
            final byte currentByte = buffer[i];
            if (currentByte == 0) {
                break;
            }
            if (currentByte == (byte) ' ' || currentByte == '0') {
                continue;
            }
            if (currentByte < '0' || currentByte > '7'){
                throw new IllegalArgumentException(
                        exceptionMessage(buffer, offset, length, start, currentByte));
            }
            result = (result << 3) + (currentByte - '0'); // convert from ASCII
        }
        return result;
    }
