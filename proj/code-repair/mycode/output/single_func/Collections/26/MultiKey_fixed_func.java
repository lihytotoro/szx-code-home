    private Object readResolve() throws Exception {
        calculateHashCode(keys);
        return this;
    }
