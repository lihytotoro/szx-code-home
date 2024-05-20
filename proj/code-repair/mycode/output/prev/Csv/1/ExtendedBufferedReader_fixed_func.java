    public int read() throws IOException {
        int current = super.read();
        if (lastChar == '\n') {
            lineCounter++;
        }
        lastChar = current;
        return lastChar;
    }
