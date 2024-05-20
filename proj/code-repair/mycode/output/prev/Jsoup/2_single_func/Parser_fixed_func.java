    private void parseStartTag() {
        tq.consume("<");
        String tagName = tq.consumeWord();
    
        if (tagName.length() == 0) { // doesn't look like a start tag after all; put < back on stack and handle as text
            tq.addFirst("&lt;");
            parseTextNode();
            return;
        }
    
        Attributes attributes = new Attributes();
        while (!tq.matchesAny("<", "/>", ">") && !tq.isEmpty()) {
            Attribute attribute = parseAttribute();
            if (attribute != null)
                attributes.put(attribute);
        }
    
        Tag tag = Tag.valueOf(tagName);
        Element child = new Element(tag, baseUri, attributes);
    
        boolean isEmptyElement = tag.isEmpty(); // empty element if empty tag (e.g. img) or self-closed el (<div/>
        if (tq.matchChomp("/>")) { // close empty element or tag
            isEmptyElement = true;
        } else {
            tq.matchChomp(">");
        }
        addChildToParent(child, isEmptyElement);
    
        // pc data only tags (textarea, script): chomp to end tag, add content as text node
        if (tag.isData() || tag.equals(titleTag) || tag.equals(textareaTag)) {
            String data = tq.chompTo("</" + tagName);
            tq.chompTo(">");
    
            Node dataNode;
            if (tag.isData()) {
                dataNode = new DataNode(data, baseUri);
            } else {
                dataNode = TextNode.createFromEncoded(data, baseUri);
            }
            child.appendChild(dataNode);
        }
    
        // <base href>: update the base uri
        if (child.tagName().equals("base")) {
            String href = child.absUrl("href");
            if (href.length() != 0) { // ignore <base target> etc
                baseUri = href;
                doc.setBaseUri(href); // set on the doc so doc.createElement(Tag) will get updated base
            }
        }
    }