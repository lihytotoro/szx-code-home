    public ArchiveInputStream createArchiveInputStream(final InputStream in)
            throws ArchiveException {
        if (in == null) {
            throw new IllegalArgumentException("Stream must not be null.");
        }
        if (!in.markSupported()) {
            throw new IllegalArgumentException("Mark is not supported.");
        }
        final byte[] signature = new byte[12];
        in.mark(signature.length);
        try {
            int signatureLength = in.read(signature);
            in.reset();
            if (ZipArchiveInputStream.matches(signature, signatureLength)) {
                return new ZipArchiveInputStream(in);
            } else if (JarArchiveInputStream.matches(signature, signatureLength)) {
                return new JarArchiveInputStream(in);
            } else if (ArArchiveInputStream.matches(signature, signatureLength)) {
                return new ArArchiveInputStream(in);
            } else if (CpioArchiveInputStream.matches(signature, signatureLength)) {
                return new CpioArchiveInputStream(in);
            }
            final byte[] dumpsig = new byte[32];
            in.mark(dumpsig.length);
            signatureLength = in.read(dumpsig);
            in.reset();
            if (DumpArchiveInputStream.matches(dumpsig, signatureLength)) {
                return new DumpArchiveInputStream(in);
            }
            final byte[] tarheader = new byte[512];
            in.mark(tarheader.length);
            signatureLength = in.read(tarheader);
            in.reset();
            if (TarArchiveInputStream.matches(tarheader, signatureLength)) {
                return new TarArchiveInputStream(in);
            }
           try {
                TarArchiveInputStream tais = new TarArchiveInputStream(new ByteArrayInputStream(tarheader));
                tais.getNextEntry();
                return new TarArchiveInputStream(in);
            } catch (Exception e) {
            }
        } catch (IOException e) {
            throw new ArchiveException("Could not use reset and mark operations.", e);
        }
        throw new ArchiveException("No Archiver found for the stream signature");
    }
