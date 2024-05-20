public static double sqrt(double x, double epsilon) {
    double approx = x / 2f;
    while (Math.abs(x-approx) > epsilon) {
        approx = 0.5f * (approx + x / approx);
    }
    return approx;
}
