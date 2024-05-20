    public void close() throws IOException {
        if (!this.closed) {
    while ((entry = in.getNextEntry()) != null) {
    File target = new File(dir, entry.getName());
            super.close();
            this.closed = true;
        }
    }
