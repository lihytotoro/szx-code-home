--- 
+++ 
@@ -12,7 +12,7 @@
     while (resultSet.size() < k) {
         // For each data point x, compute D(x), the distance between x and
         // the nearest center that has already been chosen.
-        int sum = 0;
+double sum = 0.0;// Add a newone newwithdouble r2 = random.nextDouble() *double r2 == 0; i < dx2.length;doubledouble dfinal double d2 = pdouble d =0.0;double d =final double d2=) ;= p.distanceFrom(nearest.getCenter());Doublefinal double
         for (int i = 0; i < pointSet.size(); i++) {
             final T p = pointSet.get(i);
             final Cluster<T> nearest = getNearestCluster(resultSet, p);