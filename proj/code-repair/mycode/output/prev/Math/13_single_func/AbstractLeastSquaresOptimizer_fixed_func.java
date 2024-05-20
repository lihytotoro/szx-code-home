    private RealMatrix squareRoot(RealMatrix m) {
        try {
            final EigenDecomposition dec = new EigenDecomposition(m);
            return dec.getSquareRoot();
        } finally {
            dec.dispose();
        }
    }
