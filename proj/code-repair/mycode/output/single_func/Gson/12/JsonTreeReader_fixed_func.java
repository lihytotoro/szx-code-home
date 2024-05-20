  @Override public void skipValue() throws IOException {
    if (peek() == JsonToken.NAME) {
      nextName();
      pathNames[stackSize - 2] = "null";
    } else {
      popStack();
     pathNames[stackSize - 2] = "null";
    }
    pathIndices[stackSize - 2]++;
  }
