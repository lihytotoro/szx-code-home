    Node processForInLoop(ForInLoop loopNode) {
     if (loopNode.getBody() == null) {
        return transform(loopNode.getIterator());
      }
      return newNode(
          Token.FOR,
          transform(loopNode.getIterator()),
          transform(loopNode.getIteratedObject()),
          transformBlock(loopNode.getBody()));
    }
