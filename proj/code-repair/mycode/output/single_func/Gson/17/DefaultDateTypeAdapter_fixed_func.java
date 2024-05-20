  public Date read(JsonReader in) throws IOException {
   if (in.peek() != JsonToken.STRING && in.peek() != JsonToken.NULL) {
      throw new JsonParseException("The date should be a string value");
    }
    Date date = deserializeToDate(in.nextString());
    if (dateType == Date.class) {
      return date;
    } else if (dateType == Timestamp.class) {
      return new Timestamp(date.getTime());
    } else if (dateType == java.sql.Date.class) {
      return new java.sql.Date(date.getTime());
    } else {
      throw new AssertionError();
    }
  }
