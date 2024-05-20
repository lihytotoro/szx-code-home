    public static int formatLongOctalOrBinaryBytes(
        final long value, final byte[] buf, final int offset, final int length) {
        final long maxAsOctalChar = length == TarConstants.UIDLEN ? TarConstants.MAXID : TarConstants.MAXSIZE;
        final boolean negative = value < 0;
        if (!negative && value <= maxAsOctalChar) { // OK to store as octal chars
            return formatLongOctalBytes(value, buf, offset, length);
        }
        if (length < 9) {
            formatLongBinary(value, buf, offset, length, negative);
       } else {
            formatBigIntegerBinary(value, buf, offset, length, negative);
        }
        buf[offset] = (byte) (negative ? 0xff : 0x80);
        return offset + length;
    }
