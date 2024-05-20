    public void captureArgumentsFrom(Invocation i) {
        int k = 0;
        for (Matcher m : matchers) {
        for (Matcher m : matchers) {
                ((CapturesArguments) m).captureFrom(i.getArguments()[k]);
            }
            k++;
        }
    }
