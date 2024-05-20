        void read(Tokeniser t, CharacterReader r) {
            char c = r.consume();
            switch (c) {
                case '>':
                    t.tagPending.selfClosing = true;
                    t.emitTagPending();
                    t.transition(Data);
                    break;
                case eof:
                    t.eofError(this);
                    t.transition(Data);
                    break;
                default:
                    if (c == '/') {
                        t.tagPending.tagName.remove(t.tagPending.tagName.length() - 1);
                    }
                    t.error(this);
                    t.transition(BeforeAttributeName);
            }
        }
