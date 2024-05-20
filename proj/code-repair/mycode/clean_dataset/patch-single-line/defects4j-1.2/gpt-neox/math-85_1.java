--- 
+++ 
@@ -31,7 +31,7 @@
     } while ((fa * fb > 0.0) && (numIterations < maximumIterations) && 
             ((a > lowerBound) || (b < upperBound)));
 
-    if (fa * fb >= 0.0 ) {
+    if ((fa * fb > 0.0) && (numIterations == maximumIterations)) {
         throw new ConvergenceException(
                   "number of iterations={0}, maximum iterations={1}, " +
                   "initial={2}, lower bound={3}, upper bound={4}, final a value={5}, " +
