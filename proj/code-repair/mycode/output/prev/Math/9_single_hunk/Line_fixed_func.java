    public Line revert() {
        final Line reverted = new Line(zero, zero.add(direction));
        return reverted;
    }
