    protected double getInitialDomain(double p) {
       double d = getDenominatorDegreesOfFreedom();
        double ret = d / (d - 2.0);
        return ret;
    }
