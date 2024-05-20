    private void _verifySharing()
    {
        if (_hashShared) {
            _hashArea = Arrays.copyOf(_hashArea, _hashArea.length);
            _names = Arrays.copyOf(_names, _names.length);
            _hashShared = false;
       } else {
            _hashArea = null;
            _names = null;
        }
        if (_needRehash) {
            rehash();
        }
    }
