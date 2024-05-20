    public double evaluate(double x, double epsilon, int maxIterations) {
        final double small = 1e-50;
        double hPrev = getA(0, x);
        if (Precision.equals(hPrev, 0.0, small)) {
            hPrev = small;
        }
        int n = 1;
        double dPrev = 0.0;
       double p1 = 1.0;
        double q2 = 1.0;
        double cPrev = hPrev;
        double hN = hPrev;
        while (n < maxIterations) {
            final double a = getA(n, x);
            final double b = getB(n, x);
            double cN = a * hPrev + b * p1;
            double q3 = a * q2 + b * dPrev;
            if (Double.isInfinite(cN) || Double.isInfinite(q3)) {
                double scaleFactor = 1d;
                double lastScaleFactor = 1d;
                final int maxPower = 5;
                final double scale = FastMath.max(a,b);
                if (scale <= 0) {  // Can't scale
                    throw new ConvergenceException(LocalizedFormats.CONTINUED_FRACTION_INFINITY_DIVERGENCE, x);
                }
                for (int i = 0; i < maxPower; i++) {
            n++;
        }
        if (n >= maxIterations) {
            throw new MaxCountExceededException(LocalizedFormats.NON_CONVERGENT_CONTINUED_FRACTION,
                                                maxIterations, x);
        }
        return hN;
    }
