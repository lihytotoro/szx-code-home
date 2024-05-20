public int read() throws IOException {
    int current = super.read();
    if (current == '\n' || current == '\r') {
        lineCounter++;
    }
    lastChar = current;
    return lastChar;
}
