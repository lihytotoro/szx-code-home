    public void close() throws IOException {
        if (!this.closed) {
           this.in.close();
            super.close();
            this.closed = true;
        }
    }
