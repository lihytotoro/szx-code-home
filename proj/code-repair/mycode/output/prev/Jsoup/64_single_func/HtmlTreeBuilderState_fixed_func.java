    private static void handleRawtext(Token.StartTag startTag, HtmlTreeBuilder tb) {
        if (startTag.getName().equals("style") && startTag.getAttributes().isEmpty()) {
            tb.insert(startTag);
            tb.tokeniser.transition(TokeniserState.Rawtext);
            tb.markInsertionMode();
        } else {
            tb.transition(Text);
        }
    }
