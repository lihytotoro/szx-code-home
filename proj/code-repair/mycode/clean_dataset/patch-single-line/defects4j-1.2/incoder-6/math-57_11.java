--- 
+++ 
@@ -12,7 +12,10 @@
     while (resultSet.size() < k) {
         // For each data point x, compute D(x), the distance between x and
         // the nearest center that has already been chosen.
-        int sum = 0;
+        double sum = 0;
+        for (int i = 0; i < dx2.length; i++) {
+            dx2[i] = 0;
+        }
         for (int i = 0; i < pointSet.size(); i++) {
             final T p = pointSet.get(i);
             final Cluster<T> nearest = getNearestCluster(resultSet, p);