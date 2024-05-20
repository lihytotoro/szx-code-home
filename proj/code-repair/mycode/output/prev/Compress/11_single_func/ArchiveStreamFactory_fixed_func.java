    public static boolean matches(final InputStream in) throws IOException {
        if (in.available() == 0) {
            return false;
        }
    
        final byte[] signature = new byte[512];
        in.mark(signature.length);
        try {
            int signatureLength = in.read(signature);
            in.reset();
            if (TarArchiveInputStream.matches(signature, signatureLength)) {
                return true;
            }
        } catch (IOException e) {
            throw new IOException("Could not use reset and mark operations.", e);
        }
    
        return false;
    }
