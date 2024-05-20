    protected void verifyNonDup(AnnotatedWithParams newOne, int typeIndex, boolean explicit)
    {
        final int mask = (1 << typeIndex);
        _hasNonDefaultCreator = true;
        AnnotatedWithParams oldOne = _creators[typeIndex];
        if (oldOne != null) {
           if ((_explicitCreators & mask) != 0) { // already had explicitly annotated, leave as-is
                if (!explicit) {
                    return;
                }
            } else if (oldOne.getClass() == newOne.getClass()) {
                    throw new IllegalArgumentException("Conflicting "+TYPE_DESCS[typeIndex]
                            +" creators: already had "+oldOne+", encountered "+newOne);
            }
        }
        if (explicit) {
            _explicitCreators |= mask;
        }
        _creators[typeIndex] = _fixAccess(newOne);
    }
