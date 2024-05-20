    public static long parseOctal(final byte[] buffer, final int offset, final int length) {
        long    result = 0;
        int     end = offset + length;
        int     start = offset;
        if (length < 2){
            throw new IllegalArgumentException("Length "+length+" must be at least 2");
        }
        if (buffer[start] == 0) {
            return 0L;
        }
        while (start < end){
            if (buffer[start] == ' '){
                start++;
            } else {
                break;
            }
        }
        byte trailer = buffer[end - 1];
       if (trailer == ' ' || trailer == 0){
            end--;
        } else {
            throw new IllegalArgumentException(
                    exceptionMessage(buffer, offset, length, end-1, trailer));
        }
        trailer = buffer[end - 1];
        while (start < end - 1 && (trailer == ' ' || trailer == 0)) {
            end--;
            trailer = buffer[end - 1];
        }
        for ( ;start < end; start++) {
            final byte currentByte = buffer[start];
            if (currentByte < '0' || currentByte > '7'){
                throw new IllegalArgumentException(
                        exceptionMessage(buffer, offset, length, start, currentByte));
            }
            result = (result << 3) + (currentByte - '0'); // convert from ASCII
        }
        return result;
    }
