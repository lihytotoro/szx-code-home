    public char[] getTextBuffer()
    {
        if (_inputStart >= 0) return _inputBuffer;
        if (_resultArray != null)  return _resultArray;
        if (_resultString != null) {
            return (_resultArray = _resultString.toCharArray());
        }
       if (!_hasSegments)  return null;
        return contentsAsArray();
    }
