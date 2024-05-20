    private RealMatrix squareRoot(RealMatrix m) {
           final SingularValueDecomposition dec = new SingularValueDecomposition(m);
            return dec.getS();
    }
