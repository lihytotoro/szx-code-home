    public Fraction reduce() {
        int gcd = greatestCommonDivisor(Math.abs(numerator), denominator);
        if (gcd == 1) {
            return this;
        }
        numerator /= gcd;
        denominator /= gcd;
        return this;
    }
