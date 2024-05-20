        public double[] repairAndDecode(final double[] x) {
            double[] result = decode(x);
            for (int i = 0; i < result.length; i++) {
                if (result[i] > upper[i]) {
                    result[i] = upper[i];
                } else if (result[i] < lower[i]) {
                    result[i] = lower[i];
                }
            }
            return result;
        }
