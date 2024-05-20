    private void normalise(Element element) {
        List<Node> toMove = new ArrayList<Node>();
        for (Node node: element.childNodes) {
            if (node instanceof TextNode) {
                TextNode tn = (TextNode) node;
                if (!tn.isBlank())
                    toMove.add(tn);
            }
        }
    
        for (Node node: toMove) {
            element.removeChild(node);
            element.normalize();
            body().appendChild(new TextNode(" ", ""));
            body().appendChild(node);
        }
    }
