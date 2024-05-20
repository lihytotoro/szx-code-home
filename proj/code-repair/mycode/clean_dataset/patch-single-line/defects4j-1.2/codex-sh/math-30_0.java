--- 
+++ 
@@ -3,7 +3,8 @@
                                          final int n2)
     throws ConvergenceException, MaxCountExceededException {
 
-    final int n1n2prod = n1 * n2;
+    // http://en.wikipedia.org/wiki/Mann%E2%80%93Whitney_U#Normal_approximation
+    final double n1n2prod = n1 * n2;
 
     // http://en.wikipedia.org/wiki/Mann%E2%80%93Whitney_U#Normal_approximation
     final double EU = n1n2prod / 2.0;
