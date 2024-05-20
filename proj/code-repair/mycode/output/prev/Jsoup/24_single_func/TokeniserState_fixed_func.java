        void anythingElse(Tokeniser t, CharacterReader r) {
            if (r.matchesAny('"', '\'')) {
                t.tagPending.appendTagName(r.consumeLetterSequence().toLowerCase());
                t.dataBuffer.append(r.consumeLetterSequence());
                r.advance();
                return;
            }
            // ...
        }
