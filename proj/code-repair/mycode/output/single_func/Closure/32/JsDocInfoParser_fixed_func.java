  private ExtractionInfo extractMultilineTextualBlock(JsDocToken token,
                                                      WhitespaceOption option) {
    if (token == JsDocToken.EOC || token == JsDocToken.EOL ||
        token == JsDocToken.EOF) {
      return new ExtractionInfo("", token);
    }
    stream.update();
    int startLineno = stream.getLineno();
    int startCharno = stream.getCharno() + 1;
    String line = stream.getRemainingJSDocLine();
    if (option != WhitespaceOption.PRESERVE) {
      line = line.trim();
    }
    StringBuilder builder = new StringBuilder();
    builder.append(line);
    state = State.SEARCHING_ANNOTATION;
    token = next();
    boolean ignoreStar = false;
   do {
      switch (token) {
        case STAR:
          if (ignoreStar) {
          } else {
            if (builder.length() > 0) {
              builder.append(' ');
            }
            builder.append('*');
          }
          token = next();
          continue;
        case EOL:
          if (option != WhitespaceOption.SINGLE_LINE) {
            builder.append("\n");
          }
          ignoreStar = true;
          token = next();
          continue;
        default:
          ignoreStar = false;
          state = State.SEARCHING_ANNOTATION;
          if (token == JsDocToken.EOC ||
              token == JsDocToken.EOF ||
              (token == JsDocToken.ANNOTATION &&
               option != WhitespaceOption.PRESERVE)) {
            String multilineText = builder.toString();
            if (option != WhitespaceOption.PRESERVE) {
              multilineText = multilineText.trim();
            }
            int endL
          builder.append(toString(token));
          line = stream.getRemainingJSDocLine();
          if (option != WhitespaceOption.PRESERVE) {
            line = trimEnd(line);
          }
          builder.append(line);
          token = next();
      }
    } while (true);
  }
