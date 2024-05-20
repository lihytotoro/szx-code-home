    public void captureArgumentsFrom(Invocation invocation) {
        if (invocation.getMethod().isVarArgs()) {
            int indexOfVararg = invocation.getRawArguments().length - 1;
           if (invocation.getRawArguments()[indexOfVararg] == null) {
                throw new UnsupportedOperationException();
            }
            ((CapturesArguments) matchers.get(indexOfVararg)).captureFrom(invocation.getRawArguments()[indexOfVararg]);
        } else {
            for (int position = 0; position < matchers.size(); position++) {
                Matcher m = matchers.get(position);
                if (m instanceof CapturesArguments) {
                    ((CapturesArguments) m).captureFrom(invocation.getArgumentAt(position, Object.class));
                }
            }
        }
    }
