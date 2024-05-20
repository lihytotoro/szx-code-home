    void insert(Token.Comment commentToken) {
        Comment comment = new Comment(commentToken.getData());
        Node insert = comment;
        if (commentToken.bogus) { // xml declarations are emitted as bogus comments (which is right for html, but not xml)
            String data = comment.getData();
            if (data.length() > 1 && (data.startsWith("!") || data.startsWith("?"))) {
                Document doc = Jsoup.parse("<" + data.substring(1, data.length() -1) + ">", baseUri, Parser.xmlParser());
               Element el = doc.child(0);
                if (el != null) {
                    insert = new XmlDeclaration(settings.normalizeTag(el.tagName()), data.startsWith("!"));
                    insert.attributes().addAll(el.attributes());
                }
            }
        }
        insertNode(insert);
    }
