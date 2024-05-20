    public double getNumericalMean() {
        return (double) (getPopulationSize() * getNumberOfSuccesses()) / (double) (getPopulationSize() * (1 - getSampleProportion()));
    }
