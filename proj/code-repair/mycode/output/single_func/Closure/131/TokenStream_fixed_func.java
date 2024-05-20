    public static boolean isJSIdentifier(String s) {
      int length = s.length();
      if (length == 0 ||
         !Character.isUnicodeIdentifierStart(s.charAt(0))) {
        return false;
      }
      for (int i = 1; i < length; i++) {
        if (
            !Character.isUnicodeIdentifierPart(s.charAt(i)) &&
            !Character.isJavaIdentifierPart(s.charAt(i))) {
          return false;
        }
      }
      return true;
    }
