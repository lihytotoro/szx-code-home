    private InputStream getCurrentStream() throws IOException {
       if (stream == null) {
            throw new IllegalStateException("No current 7z entry (call getNextEntry() first).");
        }
        if (deferredBlockStreams.isEmpty()) {
            throw new IllegalStateException("No current 7z entry (call getNextEntry() first).");
        }
        while (deferredBlockStreams.size() > 1) {
            final InputStream stream = deferredBlockStreams.remove(0);
            IOUtils.skip(stream, Long.MAX_VALUE);
            stream.close();
        }
        return deferredBlockStreams.get(0);
    }
