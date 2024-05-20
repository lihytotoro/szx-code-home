    public static double distance(int[] p1, int[] p2) {
      int sum = 0;
      for (int i = 0; i < p1.length; i++) {
          final int dp = p1[i] - p2[i];
          sum += dp * dp;
      }
      return Math.sqrt(sum);
    }
    
    public static List<Cluster<EuclideanIntegerPoint>> cluster(List<EuclideanIntegerPoint> points, int k, int maxIterations) {
      if (points == null || points.isEmpty()) {
        throw new IllegalArgumentException("points cannot be null or empty");
      }
      // ...
    }
