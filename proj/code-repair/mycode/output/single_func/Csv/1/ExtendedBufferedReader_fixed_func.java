    public int read() throws IOException {
        int current = super.read();
       if (current != -1 && current == '\n') {
            lineCounter++;
        }
        lastChar = current;
        return lastChar;
    }
