    protected final double doSolve() {
        // Get initial solution
        double x0 = getMin();
        double x1 = getMax();
        double f0 = computeObjectiveValue(x0);
        double f1 = computeObjectiveValue(x1);
    
        // If one of the bounds is the exact root, return it. Since these are
        // not under-approximations or over-approximations, we can return them
        // regardless of the allowed solutions.
        if (f0 == 0.0) {
            return x0;
        }
        if (f1 == 0.0) {
            return x1;
        }
    
        // Verify bracketing of initial solution.
        verifyBracketing(x0, x1);
    
        // Get accuracies.
        final double ftol = getFunctionValueAccuracy();
        final double atol = getAbsoluteAccuracy();
        final double rtol = getRelativeAccuracy();
    
        // Keep track of inverted intervals, meaning that the left bound is
        // larger than the right bound.
        boolean inverted = false;
    
        // Keep finding better approximations.
        while (true) {
            // Calculate the next approximation.
            final double x = x1 - ((f1 * (x1 - x0)) / (f1 - f0));
            final double fx = computeObjectiveValue(x);
    
            // If the new approximation is the exact root, return it. Since
            // this is not an under-approximation or an over-approximation,
            // we can return it regardless of the allowed solutions.
            if (fx == 0.0) {
                return x;
            }
    
            // Update the bounds with the new approximation.
            if (f1 * fx < 0) {
                // The value of x1 has switched to the other bound, thus inverting
                // the interval.
                x0 = x1;
                f0 = f1;
                inverted = !inverted;
            } else {
                switch (method) {
                case ILLINOIS:
                    f0 *= 0.5;
                    break;
                case PEGASUS:
                    f0 *= f1 / (f1 + fx);
                    break;
                case REGULA_FALSI:
                    // Detect early that algorithm is stuck, instead of waiting
                    // for the maximum number of iterations to be exceeded.
                    break;
                default:
                    // Should never happen.
                    throw new MathInternalError();
                }
            }
            // Update from [x0, x1] to [x0, x].
            x1 = x;
            f1 = fx;
    
            // If the current interval is within the given accuracies, we
            // are satisfied with the current approximation.
            if (FastMath.abs(x1 - x0) < FastMath.max(rtol * FastMath.abs(x1),
                                                     atol)) {
                switch (allowed) {
                case ANY_SIDE:
                    return x1;
                case LEFT_SIDE:
                    return inverted ? x1 : x0;
                case RIGHT_SIDE:
                    return inverted ? x0 : x1;
                case BELOW_SIDE:
                    return (f1 <= 0) ? x1 : x0;
                case ABOVE_SIDE:
                    return (f1 >= 0) ? x1 : x0;
                default:
                    throw new MathInternalError();
                }
            }
        }
    }
