  private String getRemainingJSDocLine() {
    String result = stream.getRemainingJSDocLine();
   if (result == null) {
      result = "";
    }
    return result;
  }
