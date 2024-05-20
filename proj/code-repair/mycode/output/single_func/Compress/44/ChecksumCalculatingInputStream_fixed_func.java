    public ChecksumCalculatingInputStream(final Checksum checksum, final InputStream in) {
       if (checksum == null || in == null) {
            throw new NullPointerException();
        }
        this.checksum = checksum;
        this.in = in;
    }
